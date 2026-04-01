from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.auth.presentation.dependencies import get_current_admin
from app.modules.auth.presentation.schemas.auth import UserResponse
from app.modules.categories.application.services.category_service import CategoryService
from app.modules.categories.domain.exceptions import CategoryNameExistsError
from app.modules.categories.presentation.deps import get_category_service
from app.modules.categories.presentation.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    body: CategoryCreate,
    _: UserResponse = Depends(get_current_admin),
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    try:
        cat = service.create(body.name)
        return CategoryResponse.model_validate(cat)
    except CategoryNameExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=exc.message,
        ) from exc


@router.get("", response_model=list[CategoryResponse])
def list_categories(
    service: CategoryService = Depends(get_category_service),
) -> list[CategoryResponse]:
    rows = service.list_all()
    return [CategoryResponse.model_validate(r) for r in rows]
