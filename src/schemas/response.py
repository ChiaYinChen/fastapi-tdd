"""Wrapper for API Responses."""

from typing import Generic, TypeVar

from pydantic import BaseModel

ModelType = TypeVar("ModelType")


class GenericResponse(BaseModel, Generic[ModelType]):
    """Generic wrapper for API responses."""

    message: str | None = None
    data: list[ModelType] | ModelType | None = None
