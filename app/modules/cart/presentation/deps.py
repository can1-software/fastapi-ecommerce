from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.cart.application.services.cart_service import CartService
from app.modules.cart.infrastructure.repositories.cart_repository import CartRepository
from app.modules.products.infrastructure.repositories.product_repository import ProductRepository


def get_cart_repository(db: Session = Depends(get_db)) -> CartRepository:
    return CartRepository(db)


def get_product_repository_for_cart(db: Session = Depends(get_db)) -> ProductRepository:
    return ProductRepository(db)


def get_cart_service(
    cart_repo: CartRepository = Depends(get_cart_repository),
    product_repo: ProductRepository = Depends(get_product_repository_for_cart),
) -> CartService:
    return CartService(cart_repo, product_repo)
