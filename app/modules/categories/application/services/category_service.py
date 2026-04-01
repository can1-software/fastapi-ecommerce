from app.modules.categories.domain.exceptions import CategoryNameExistsError
from app.modules.categories.infrastructure.repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self, repo: CategoryRepository) -> None:
        self._repo = repo

    def create(self, name: str):
        normalized = name.strip()
        if self._repo.get_by_name(normalized):
            raise CategoryNameExistsError()
        return self._repo.create(name=normalized)

    def list_all(self):
        return self._repo.list_all()
