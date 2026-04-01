class CartItemNotFoundError(Exception):
    def __init__(self, message: str = "Cart item not found") -> None:
        self.message = message
        super().__init__(message)


class ProductOutOfStockError(Exception):
    def __init__(self, message: str = "Requested quantity exceeds stock") -> None:
        self.message = message
        super().__init__(message)
