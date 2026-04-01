from decimal import Decimal

from app.modules.cart.domain.exceptions import CartItemNotFoundError, ProductOutOfStockError
from app.modules.cart.infrastructure.repositories.cart_repository import CartRepository
from app.modules.cart.presentation.schemas.cart import CartItemResponse, CartResponse
from app.modules.products.domain.exceptions import ProductNotFoundError
from app.modules.products.infrastructure.repositories.product_repository import ProductRepository


class CartService:
    def __init__(self, cart_repo: CartRepository, product_repo: ProductRepository) -> None:
        self._carts = cart_repo
        self._products = product_repo

    def _get_or_create_cart(self, user_id: int):
        cart = self._carts.get_by_user_id(user_id)
        if cart is None:
            cart = self._carts.create_for_user(user_id)
            cart = self._carts.get_by_user_id(user_id)
        return cart

    def add(self, user_id: int, product_id: int, quantity: int) -> CartResponse:
        product = self._products.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError()

        cart = self._get_or_create_cart(user_id)
        if cart is None:
            raise RuntimeError("Could not create cart")

        existing_qty = 0
        for item in cart.items:
            if item.product_id == product_id:
                existing_qty = item.quantity
                break
        if existing_qty + quantity > product.stock:
            raise ProductOutOfStockError()

        self._carts.add_or_increase_item(cart, product_id, quantity)
        return self.get_cart(user_id)

    def remove(self, user_id: int, product_id: int) -> CartResponse:
        cart = self._get_or_create_cart(user_id)
        if cart is None:
            raise RuntimeError("Could not create cart")
        deleted = self._carts.remove_item(cart.id, product_id)
        if not deleted:
            raise CartItemNotFoundError()
        return self.get_cart(user_id)

    def update(self, user_id: int, product_id: int, quantity: int) -> CartResponse:
        cart = self._get_or_create_cart(user_id)
        if cart is None:
            raise RuntimeError("Could not create cart")

        if quantity == 0:
            deleted = self._carts.remove_item(cart.id, product_id)
            if not deleted:
                raise CartItemNotFoundError()
            return self.get_cart(user_id)

        product = self._products.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError()
        if quantity > product.stock:
            raise ProductOutOfStockError()

        updated = self._carts.update_item_quantity(cart.id, product_id, quantity)
        if updated is None:
            raise CartItemNotFoundError()
        return self.get_cart(user_id)

    def get_cart(self, user_id: int) -> CartResponse:
        cart = self._get_or_create_cart(user_id)
        if cart is None:
            raise RuntimeError("Could not create cart")
        items: list[CartItemResponse] = []
        total = Decimal("0")
        for item in cart.items:
            line = item.product.price * item.quantity
            items.append(
                CartItemResponse(
                    product_id=item.product_id,
                    name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity,
                    total_price=line,
                )
            )
            total += line
        return CartResponse(items=items, total_cart_price=total)
