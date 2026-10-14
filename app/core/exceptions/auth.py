from fastapi import HTTPException, status


class AuthenticationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidCredentialsError(AuthenticationError):
    def __init__(self):
        super().__init__("Incorrect username or password")


class InvalidTokenError(AuthenticationError):
    def __init__(self):
        super().__init__("Token has expired or is invalid")


class InvalidTokenTypeError(AuthenticationError):
    def __init__(self):
        super().__init__("Invalid token type")


class UserNotFoundError(AuthenticationError):
    def __init__(self):
        super().__init__("User not found")


class MissingTokenError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing token",
        )
