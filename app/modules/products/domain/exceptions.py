class ProductNotFoundError(Exception):
    def __init__(self, message: str = "Product not found") -> None:
        self.message = message
        super().__init__(message)


class InvalidCategoryError(Exception):
    def __init__(self, message: str = "Invalid category") -> None:
        self.message = message
        super().__init__(message)
