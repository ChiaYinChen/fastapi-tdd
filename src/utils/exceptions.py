"""Custom exception classes for the application.

This module defines a base `CustomError` class and several specific
exception types that inherit from it. These exceptions are used to represent
various error conditions within the application, typically those that
should result in specific HTTP error responses.
"""
from typing import Any


class CustomError(Exception):
    """Base class for custom application errors.

    Attributes:
        status_code (int): The HTTP status code associated with this error.
        error_code (str): A specific error code string for this error type.
        message (Any): The error message or detailed information.
    """
    def __init__(self, status_code: int, error_code: str, message: Any):
        """Initializes the CustomError.

        Args:
            status_code (int): The HTTP status code.
            error_code (str): The specific error code.
            message (Any): The error message.
        """
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        super().__init__(message)


class UnauthenticatedError(CustomError):
    """Exception raised for unauthenticated requests (HTTP 401).

    Attributes:
        status_code (int): Always 401.
        error_code (str): Specific error code for unauthenticated access.
        message (Any): Error message.
    """
    def __init__(self, error_code: str, message: Any):
        """Initializes UnauthenticatedError.

        Args:
            error_code (str): The specific error code.
            message (Any): The error message.
        """
        super().__init__(status_code=401, error_code=error_code, message=message)


class UnauthorizedError(CustomError):
    """Exception raised for unauthorized requests (HTTP 403).

    Indicates that the authenticated user does not have permission
    to perform the requested action.

    Attributes:
        status_code (int): Always 403.
        error_code (str): Specific error code for unauthorized access.
        message (Any): Error message.
    """
    def __init__(self, error_code: str, message: Any):
        """Initializes UnauthorizedError.

        Args:
            error_code (str): The specific error code.
            message (Any): The error message.
        """
        super().__init__(status_code=403, error_code=error_code, message=message)


class ConflictError(CustomError):
    """Exception raised when a request conflicts with current state (HTTP 409).

    For example, trying to create a resource that already exists.

    Attributes:
        status_code (int): Always 409.
        error_code (str): Specific error code for resource conflict.
        message (Any): Error message.
    """
    def __init__(self, error_code: str, message: Any):
        """Initializes ConflictError.

        Args:
            error_code (str): The specific error code.
            message (Any): The error message.
        """
        super().__init__(status_code=409, error_code=error_code, message=message)


class NotFoundError(CustomError):
    """Exception raised when a requested resource is not found (HTTP 404).

    Attributes:
        status_code (int): Always 404.
        error_code (str): Specific error code for resource not found.
        message (Any): Error message.
    """
    def __init__(self, error_code: str, message: Any):
        """Initializes NotFoundError.

        Args:
            error_code (str): The specific error code.
            message (Any): The error message.
        """
        super().__init__(status_code=404, error_code=error_code, message=message)


class BadRequestError(CustomError):
    """Exception raised for malformed or invalid requests (HTTP 400).

    Attributes:
        status_code (int): Always 400.
        error_code (str): Specific error code for bad requests.
        message (Any): Error message.
    """
    def __init__(self, error_code: str, message: Any):
        """Initializes BadRequestError.

        Args:
            error_code (str): The specific error code.
            message (Any): The error message.
        """
        super().__init__(status_code=400, error_code=error_code, message=message)


class InternalServerError(CustomError):
    """Exception raised for unexpected internal server errors (HTTP 500).

    Attributes:
        status_code (int): Always 500.
        error_code (str): Specific error code for internal server errors.
        message (Any): Error message.
    """
    def __init__(self, error_code: str, message: Any):
        """Initializes InternalServerError.

        Args:
            error_code (str): The specific error code.
            message (Any): The error message.
        """
        super().__init__(status_code=500, error_code=error_code, message=message)
