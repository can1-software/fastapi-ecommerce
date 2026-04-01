from decimal import Decimal

from app.modules.categories.infrastructure.repositories.category_repository import CategoryRepository
from app.modules.products.domain.exceptions import InvalidCategoryError, ProductNotFoundError
from app.modules.products.infrastructure.image_storage import delete_product_image_file
from app.modules.products.infrastructure.persistence.models.product import Product
from app.modules.products.infrastructure.repositories.product_repository import ProductRepository
from app.modules.products.presentation.schemas.product import ProductListResponse, ProductResponse


class ProductService:
    def __init__(
        self,
        product_repo: ProductRepository,
        category_repo: CategoryRepository,
    ) -> None:
        self._products = product_repo
        self._categories = category_repo

    def _ensure_category(self, category_id: int) -> None:
        if self._categories.get_by_id(category_id) is None:
            raise InvalidCategoryError()

    def create(
        self,
        *,
        name: str,
        description: str | None,
        price: Decimal,
        stock: int,
        image: str | None,
        category_id: int,
    ) -> Product:
        self._ensure_category(category_id)
        row = self._products.create(
            name=name,
            description=description,
            price=price,
            stock=stock,
            image=image,
            category_id=category_id,
        )
        loaded = self._products.get_by_id(row.id)
        if loaded is None:
            raise ProductNotFoundError()
        return loaded

    def get_by_id(self, product_id: int) -> Product:
        p = self._products.get_by_id(product_id)
        if p is None:
            raise ProductNotFoundError()
        return p

    def update(
        self,
        product_id: int,
        *,
        name: str | None,
        description: str | None,
        price: Decimal | None,
        stock: int | None,
        image: str | None,
        category_id: int | None,
        update_image: bool = False,
    ) -> Product:
        p = self._products.get_by_id(product_id)
        if p is None:
            raise ProductNotFoundError()
        if category_id is not None:
            self._ensure_category(category_id)
        self._products.update(
            p,
            name=name,
            description=description,
            price=price,
            stock=stock,
            image=image,
            category_id=category_id,
            update_image=update_image,
        )
        loaded = self._products.get_by_id(product_id)
        if loaded is None:
            raise ProductNotFoundError()
        return loaded

    def delete(self, product_id: int) -> None:
        p = self._products.get_by_id(product_id)
        if p is None:
            raise ProductNotFoundError()
        delete_product_image_file(p.image)
        self._products.delete(p)

    def list_products(
        self,
        *,
        category_id: int | None,
        min_price: Decimal | None,
        max_price: Decimal | None,
        search: str | None,
        limit: int,
        offset: int,
    ) -> ProductListResponse:
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValueError("min_price cannot be greater than max_price")
        rows, total = self._products.list_filtered(
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            search=search,
            limit=limit,
            offset=offset,
        )
        items = [ProductResponse.from_product(r) for r in rows]
        return ProductListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )
