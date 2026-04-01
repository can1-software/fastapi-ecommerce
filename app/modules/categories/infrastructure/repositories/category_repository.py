from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.categories.infrastructure.persistence.models.category import Category


class CategoryRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, category_id: int) -> Category | None:
        return self._db.get(Category, category_id)

    def get_by_name(self, name: str) -> Category | None:
        stmt = select(Category).where(Category.name == name)
        return self._db.execute(stmt).scalar_one_or_none()

    def list_all(self) -> list[Category]:
        stmt = select(Category).order_by(Category.name)
        return list(self._db.execute(stmt).scalars().all())

    def create(self, *, name: str) -> Category:
        row = Category(name=name.strip())
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row
