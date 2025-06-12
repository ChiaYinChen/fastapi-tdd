"""Pydantic schemas for account-related operations.

This module defines Pydantic models used for creating, updating,
and representing user accounts, as well as for password reset operations.
These schemas are utilized for request validation, response serialization,
and data interaction within the application.
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer, field_validator

from ..core.security import get_password_hash
from ..schemas.common import DateTimeAnnotation


class AccountCreate(BaseModel):
    """Schema for creating a new user account.

    Used for request body validation when a new account is registered.
    It expects an email and a password (aliased as 'password' but stored
    as 'hashed_password' after validation). The name is optional.

    Attributes:
        email (EmailStr): The email address of the user.
        hashed_password (str): The user's plain text password (will be hashed).
            Aliased as 'password' in input. Minimum length of 6 characters.
        name (str | None): The optional name of the user, max length 30 characters.
    """
    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    hashed_password: str = Field(..., min_length=6, alias="password")
    name: str | None = Field(None, max_length=30)

    @field_validator("hashed_password", mode="after")
    def set_hashed_password(cls, value: str) -> str:
        """Hashes the plain text password after validation.

        Args:
            value (str): The plain text password provided.

        Returns:
            str: The hashed password.
        """
        return get_password_hash(value)


class Account(BaseModel):
    """Schema for representing a user account in API responses.

    Provides a structured representation of an account, including its ID,
    email, name, status, and timestamps.

    Attributes:
        id (UUID): The unique identifier of the account.
        email (EmailStr): The email address of the user.
        name (str | None): The name of the user.
        is_active (bool): Whether the account is currently active.
        created_at (DateTimeAnnotation): Timestamp of account creation.
        updated_at (DateTimeAnnotation): Timestamp of the last account update.
    """
    id: UUID
    email: EmailStr
    name: str | None
    is_active: bool
    created_at: DateTimeAnnotation
    updated_at: DateTimeAnnotation

    @field_serializer("created_at", "updated_at")
    def format_datetime(self, value: datetime) -> str:
        """Formats datetime fields to a specific string representation.

        Args:
            value (datetime): The datetime object to format.

        Returns:
            str: The formatted datetime string (YYYY-MM-DDTHH:MM:SS).
        """
        return value.strftime("%Y-%m-%dT%H:%M:%S")


class AccountUpdate(BaseModel):
    """Schema for updating an existing user account.

    All fields are optional. If 'password' (aliased for 'hashed_password')
    is provided, it will be hashed.

    Attributes:
        email (str | None): The new email address for the user.
        hashed_password (str | None): The new plain text password (will be hashed).
            Aliased as 'password' in input. Minimum length of 6 characters if provided.
        name (str | None): The new name for the user, max length 30 characters.
        is_active (bool | None): The new active status for the account.
    """
    model_config = ConfigDict(populate_by_name=True)

    email: str | None = None
    hashed_password: str | None = Field(None, min_length=6, alias="password") # Allow None
    name: str | None = None
    is_active: bool | None = None

    @field_validator("hashed_password", mode="after")
    def set_hashed_password(cls, value: str | None) -> str | None:
        """Hashes the plain text password after validation, if provided.

        Args:
            value (str | None): The plain text password or None.

        Returns:
            str | None: The hashed password if a password was provided, otherwise None.
        """
        if value is None:
            return None
        return get_password_hash(value)


class ResetPassword(BaseModel):
    """Schema for the data required to reset a user's password.

    Requires the user's current password and a new password.

    Attributes:
        current_password (str): The user's current password. Minimum length 6.
        new_password (str): The desired new password. Minimum length 6.
    """
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
