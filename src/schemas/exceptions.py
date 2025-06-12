"""Pydantic schemas for representing API error responses.

This module defines models for structured error responses, including detailed
validation errors and custom application errors, ensuring consistent error
reporting to API clients.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from ..constants.errors import CustomErrorCode

if TYPE_CHECKING:
    from pydantic import ValidationError


class ValidationErrorDetail(BaseModel):
    """Schema for providing detailed information about a single validation error.

    Attributes:
        location (str): The location of the error (e.g., "body -> field_name").
        message (str): A human-readable message describing the error.
        error_type (str): The type of validation error (e.g., "value_error.missing").
        context (dict[str, Any] | None): Optional context for the error.
    """
    location: str
    message: str
    error_type: str
    context: dict[str, Any] | None = None


class APIValidationError(BaseModel):
    """Schema for representing a collection of Pydantic validation errors.

    This is typically used as the response body when request validation fails.

    Attributes:
        error_code (str): A specific error code, defaults to `VALIDATE_ERROR`.
        message (str): A general message indicating validation failure.
        errors (list[ValidationErrorDetail]): A list of detailed validation errors.
    """
    error_code: str = CustomErrorCode.VALIDATE_ERROR
    message: str
    errors: list[ValidationErrorDetail]

    @classmethod
    def from_pydantic(cls, exc: ValidationError) -> APIValidationError:
        """Creates an `APIValidationError` instance from a Pydantic `ValidationError`.

        This class method transforms Pydantic's native validation exception
        into a standardized API error response structure.

        Args:
            exc (ValidationError): The Pydantic `ValidationError` instance.

        Returns:
            APIValidationError: An instance populated with details from the exception.
        """
        return cls(
            error_code=CustomErrorCode.VALIDATE_ERROR,
            message="Pydantic Validation Errors", # Corrected typo "Pydanyic"
            errors=[
                ValidationErrorDetail(
                    location=" -> ".join(str(loc_item) for loc_item in err["loc"]), # Ensure all loc_items are str
                    message=err["msg"],
                    error_type=err["type"],
                    context=err.get("ctx"),
                )
                for err in exc.errors()
            ],
        )


class CustomErrorResponse(BaseModel): # Corrected typo in class name
    """Schema for a generic custom error response.

    Used as the response body for errors raised by application-specific
    custom exceptions (subclasses of `CustomError`).

    Attributes:
        error_code (str): The specific error code from `CustomErrorCode`.
        message (Any): The error message, which can be a string or other serializable type.
    """
    error_code: str
    message: Any
