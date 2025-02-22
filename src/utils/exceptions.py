from typing import Any


class CustomError(Exception):
    def __init__(self, status_code: int, error_code: str, message: Any):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message


class UnauthenticatedError(CustomError):
    """Handle unauthenticated request."""

    def __init__(self, error_code, message):
        self.status_code = 401
        self.error_code = error_code
        self.message = message


class UnauthorizedError(CustomError):
    """Handle unauthorized request."""

    def __init__(self, error_code, message):
        self.status_code = 403
        self.error_code = error_code
        self.message = message


class ConflictError(CustomError):
    """Resource conflict error."""

    def __init__(self, error_code, message):
        self.status_code = 409
        self.error_code = error_code
        self.message = message


class NotFoundError(CustomError):
    """Resource not found error."""

    def __init__(self, error_code, message):
        self.status_code = 404
        self.error_code = error_code
        self.message = message


class BadRequestError(CustomError):
    """Handle bad request."""

    def __init__(self, error_code, message):
        self.status_code = 400
        self.error_code = error_code
        self.message = message


class InternalServerError(CustomError):
    """Internal server error exception."""

    def __init__(self, error_code, message):
        self.status_code = 500
        self.error_code = error_code
        self.message = message
