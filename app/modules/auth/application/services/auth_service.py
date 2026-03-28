from app.modules.auth.domain.exceptions import (
    EmailAlreadyRegisteredError,
    InactiveUserError,
    InvalidCredentialsError,
)
from app.modules.auth.infrastructure.persistence.models.user import User
from app.modules.auth.infrastructure.repositories.user_repository import UserRepository
from app.modules.auth.infrastructure.security import (
    create_access_token,
    hash_password,
    verify_password,
)


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    def register(self, email: str, password: str) -> User:
        normalized = email.strip().lower()
        if self._users.get_by_email(normalized):
            raise EmailAlreadyRegisteredError()
        hashed = hash_password(password)
        return self._users.create(email=normalized, hashed_password=hashed)

    def login(self, email: str, password: str) -> str:
        normalized = email.strip().lower()
        user = self._users.get_by_email(normalized)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise InactiveUserError()
        return create_access_token(user.id)
