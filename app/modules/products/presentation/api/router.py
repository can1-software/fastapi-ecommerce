from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    UploadFile,
    status,
)

from app.modules.auth.presentation.dependencies import get_current_admin
from app.modules.auth.presentation.schemas.auth import UserResponse
from app.modules.products.application.services.product_service import ProductService
from app.modules.products.domain.exceptions import InvalidCategoryError, ProductNotFoundError
from app.modules.products.infrastructure.image_storage import (
    delete_product_image_file,
    save_product_image_file,
)
from app.modules.products.presentation.deps import get_product_service
from app.modules.products.presentation.schemas.product import ProductListResponse, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    name: str = Form(..., min_length=1, max_length=255),
    price: Decimal = Form(..., gt=0),
    stock: int = Form(..., ge=0),
    category_id: int = Form(..., ge=1),
    description: str | None = Form(None),
    image: UploadFile = File(...),
    _: UserResponse = Depends(get_current_admin),
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    try:
        stored_image = await save_product_image_file(image)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    try:
        created = service.create(
            name=name,
            description=description,
            price=price,
            stock=stock,
            image=stored_image,
            category_id=category_id,
        )
        return ProductResponse.from_product(created)
    except InvalidCategoryError as exc:
        delete_product_image_file(stored_image)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc


@router.get("", response_model=ProductListResponse)
def list_products(
    service: ProductService = Depends(get_product_service),
    category_id: int | None = Query(default=None, ge=1),
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    search: str | None = Query(default=None, max_length=500),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ProductListResponse:
    try:
        return service.list_products(
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            search=search,
            limit=limit,
            offset=offset,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int = Path(ge=1),
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    try:
        p = service.get_by_id(product_id)
        return ProductResponse.from_product(p)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int = Path(ge=1),
    name: str | None = Form(None, min_length=1, max_length=255),
    description: str | None = Form(None),
    price: Decimal | None = Form(None),
    stock: int | None = Form(None),
    category_id: int | None = Form(None),
    clear_image: bool = Form(False),
    image: UploadFile | None = File(None),
    _: UserResponse = Depends(get_current_admin),
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    if price is not None and price <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="price must be greater than 0")
    if stock is not None and stock < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="stock must be >= 0")
    if category_id is not None and category_id < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="category_id must be >= 1")

    try:
        existing = service.get_by_id(product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

    update_image = False
    new_image: str | None = None

    try:
        if image is not None and image.filename:
            new_image = await save_product_image_file(image)
            delete_product_image_file(existing.image)
            update_image = True
        elif clear_image:
            new_image = None
            delete_product_image_file(existing.image)
            update_image = True
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    try:
        p = service.update(
            product_id,
            name=name,
            description=description,
            price=price,
            stock=stock,
            image=new_image,
            category_id=category_id,
            update_image=update_image,
        )
        return ProductResponse.from_product(p)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except InvalidCategoryError as exc:
        if new_image is not None:
            delete_product_image_file(new_image)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int = Path(ge=1),
    _: UserResponse = Depends(get_current_admin),
    service: ProductService = Depends(get_product_service),
) -> None:
    try:
        service.delete(product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
