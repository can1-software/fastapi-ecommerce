from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.categories.application.services.category_service import CategoryService
from app.modules.categories.infrastructure.repositories.category_repository import CategoryRepository


def get_category_repository(db: Session = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(db)


def get_category_service(
    repo: CategoryRepository = Depends(get_category_repository),
) -> CategoryService:
    return CategoryService(repo)
