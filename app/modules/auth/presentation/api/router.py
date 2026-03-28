from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.auth.domain.exceptions import (
    EmailAlreadyRegisteredError,
    InactiveUserError,
    InvalidCredentialsError,
)
from app.modules.auth.application.services.auth_service import AuthService
from app.modules.auth.presentation.deps import get_auth_service
from app.modules.auth.presentation.dependencies import get_current_user
from app.modules.auth.presentation.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    body: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    try:
        user = auth_service.register(body.email, body.password)
        return UserResponse.model_validate(user)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=exc.message,
        ) from exc


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        access_token = auth_service.login(body.email, body.password)
        return TokenResponse(access_token=access_token)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
        ) from exc
    except InactiveUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exc.message,
        ) from exc


@router.get("/me", response_model=UserResponse)
def read_me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    return current_user
