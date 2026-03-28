class EmailAlreadyRegisteredError(Exception):
    def __init__(self, message: str = "Email already registered") -> None:
        self.message = message
        super().__init__(message)


class InvalidCredentialsError(Exception):
    def __init__(self, message: str = "Incorrect email or password") -> None:
        self.message = message
        super().__init__(message)


class InactiveUserError(Exception):
    def __init__(self, message: str = "Account is inactive") -> None:
        self.message = message
        super().__init__(message)
