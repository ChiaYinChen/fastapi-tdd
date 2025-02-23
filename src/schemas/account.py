from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer

from ..schemas.common import DateTimeAnnotation


class AccountCreate(BaseModel):
    """Input schema for account creation."""

    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    hashed_password: str = Field(..., min_length=6, alias="password")
    name: str | None = Field(None, max_length=30)


class Account(BaseModel):
    """Schema for account response."""

    id: UUID
    email: EmailStr
    name: str | None
    is_active: bool
    created_at: DateTimeAnnotation
    updated_at: DateTimeAnnotation

    @field_serializer("created_at", "updated_at")
    def format_datetime(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%dT%H:%M:%S")
