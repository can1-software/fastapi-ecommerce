class CategoryNotFoundError(Exception):
    def __init__(self, message: str = "Category not found") -> None:
        self.message = message
        super().__init__(message)


class CategoryNameExistsError(Exception):
    def __init__(self, message: str = "Category name already exists") -> None:
        self.message = message
        super().__init__(message)
