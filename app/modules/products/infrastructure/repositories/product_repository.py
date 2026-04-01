from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.modules.products.infrastructure.persistence.models.product import Product


def _escape_ilike(term: str) -> str:
    return (
        term.replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, product_id: int) -> Product | None:
        stmt = (
            select(Product)
            .options(joinedload(Product.category))
            .where(Product.id == product_id)
        )
        return self._db.execute(stmt).unique().scalar_one_or_none()

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
        row = Product(
            name=name.strip(),
            description=description,
            price=price,
            stock=stock,
            image=image,
            category_id=category_id,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def update(
        self,
        product: Product,
        *,
        name: str | None,
        description: str | None,
        price: Decimal | None,
        stock: int | None,
        image: str | None,
        category_id: int | None,
        update_image: bool = False,
    ) -> Product:
        if name is not None:
            product.name = name.strip()
        if description is not None:
            product.description = description
        if price is not None:
            product.price = price
        if stock is not None:
            product.stock = stock
        if update_image:
            product.image = image
        if category_id is not None:
            product.category_id = category_id
        self._db.commit()
        self._db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self._db.delete(product)
        self._db.commit()

    def list_filtered(
        self,
        *,
        category_id: int | None,
        min_price: Decimal | None,
        max_price: Decimal | None,
        search: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Product], int]:
        base = select(Product)
        count_base = select(func.count()).select_from(Product)

        if category_id is not None:
            base = base.where(Product.category_id == category_id)
            count_base = count_base.where(Product.category_id == category_id)
        if min_price is not None:
            base = base.where(Product.price >= min_price)
            count_base = count_base.where(Product.price >= min_price)
        if max_price is not None:
            base = base.where(Product.price <= max_price)
            count_base = count_base.where(Product.price <= max_price)
        if search is not None and (t := search.strip()):
            pat = f"%{_escape_ilike(t)}%"
            base = base.where(
                or_(
                    Product.name.ilike(pat, escape="\\"),
                    Product.description.ilike(pat, escape="\\"),
                )
            )
            count_base = count_base.where(
                or_(
                    Product.name.ilike(pat, escape="\\"),
                    Product.description.ilike(pat, escape="\\"),
                )
            )

        total = int(self._db.execute(count_base).scalar_one())
        stmt = (
            base.options(joinedload(Product.category))
            .order_by(Product.id)
            .limit(limit)
            .offset(offset)
        )
        rows = list(self._db.execute(stmt).unique().scalars().all())
        return rows, total
