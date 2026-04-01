from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.modules.cart.infrastructure.persistence.models.cart import Cart
from app.modules.cart.infrastructure.persistence.models.cart_item import CartItem


class CartRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_user_id(self, user_id: int) -> Cart | None:
        stmt = (
            select(Cart)
            .options(joinedload(Cart.items).joinedload(CartItem.product))
            .where(Cart.user_id == user_id)
        )
        return self._db.execute(stmt).unique().scalar_one_or_none()

    def create_for_user(self, user_id: int) -> Cart:
        cart = Cart(user_id=user_id)
        self._db.add(cart)
        self._db.commit()
        self._db.refresh(cart)
        return cart

    def add_or_increase_item(self, cart: Cart, product_id: int, quantity: int) -> CartItem:
        stmt = select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
        )
        item = self._db.execute(stmt).scalar_one_or_none()
        if item is None:
            item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
            self._db.add(item)
        else:
            item.quantity += quantity
        self._db.commit()
        self._db.refresh(item)
        return item

    def remove_item(self, cart_id: int, product_id: int) -> bool:
        stmt = select(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id,
        )
        item = self._db.execute(stmt).scalar_one_or_none()
        if item is None:
            return False
        self._db.delete(item)
        self._db.commit()
        return True

    def update_item_quantity(self, cart_id: int, product_id: int, quantity: int) -> CartItem | None:
        stmt = select(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id,
        )
        item = self._db.execute(stmt).scalar_one_or_none()
        if item is None:
            return None
        item.quantity = quantity
        self._db.commit()
        self._db.refresh(item)
        return item
