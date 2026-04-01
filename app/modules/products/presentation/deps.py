from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.categories.infrastructure.repositories.category_repository import CategoryRepository
from app.modules.products.application.services.product_service import ProductService
from app.modules.products.infrastructure.repositories.product_repository import ProductRepository


def get_product_repository(db: Session = Depends(get_db)) -> ProductRepository:
    return ProductRepository(db)


def get_category_repository_for_products(db: Session = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(db)


def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository),
    category_repo: CategoryRepository = Depends(get_category_repository_for_products),
) -> ProductService:
    return ProductService(product_repo, category_repo)
