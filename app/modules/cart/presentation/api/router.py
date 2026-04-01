from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.modules.auth.presentation.dependencies import get_current_user
from app.modules.auth.presentation.schemas.auth import UserResponse
from app.modules.cart.application.services.cart_service import CartService
from app.modules.cart.domain.exceptions import CartItemNotFoundError, ProductOutOfStockError
from app.modules.cart.presentation.deps import get_cart_service
from app.modules.cart.presentation.schemas.cart import CartAddRequest, CartResponse, CartUpdateRequest
from app.modules.products.domain.exceptions import ProductNotFoundError

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/add", response_model=CartResponse)
def add_to_cart(
    body: CartAddRequest,
    current_user: UserResponse = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    try:
        return service.add(current_user.id, body.product_id, body.quantity)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found") from exc
    except ProductOutOfStockError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc


@router.delete("/remove/{product_id}", response_model=CartResponse)
def remove_from_cart(
    product_id: int = Path(ge=1),
    current_user: UserResponse = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    try:
        return service.remove(current_user.id, product_id)
    except CartItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.put("/update", response_model=CartResponse)
def update_cart_item(
    body: CartUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    try:
        return service.update(current_user.id, body.product_id, body.quantity)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found") from exc
    except ProductOutOfStockError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except CartItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.get("", response_model=CartResponse)
def get_cart(
    current_user: UserResponse = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    return service.get_cart(current_user.id)
