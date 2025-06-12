"""Pydantic schemas for generic API responses.

This module defines a generic response wrapper that can be used for
consistent API response structures, allowing for an optional message
and a data payload of a specified type.

Type Variables:
    ModelType: A type variable used to represent the type of the data payload
        in the generic response.
"""
from typing import Generic, TypeVar

from pydantic import BaseModel

ModelType = TypeVar("ModelType")


class GenericResponse(BaseModel, Generic[ModelType]):
    """A generic wrapper for API responses.

    This schema provides a standardized structure for API responses,
    allowing for an optional message and a data payload which can be of
    any type specified by `ModelType`.

    Type Args:
        ModelType: The type of the data payload.

    Attributes:
        message (str | None): An optional message to include in the response
            (e.g., success message). Defaults to None.
        data (list[ModelType] | ModelType | None): The actual data payload of the response.
            This can be a single object, a list of objects, or None. Defaults to None.
    """
    message: str | None = None
    data: list[ModelType] | ModelType | None = None
