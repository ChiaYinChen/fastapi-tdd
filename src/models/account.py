"""Defines the Account model for representing user accounts.

This module contains the Ormar model for user accounts, including fields for
authentication, profile information, and status tracking.
"""
from datetime import datetime
from uuid import uuid4

import ormar
from sqlalchemy.sql import expression

from ..db.session import base_ormar_config
from ..models.mixin import DateFieldsMixin


class Account(ormar.Model, DateFieldsMixin):
    """Represents a user account in the system.

    This model stores information about users, including their authentication
    credentials, personal details, and account status.

    Attributes:
        id (str): The unique identifier for the account (UUID).
        email (str): The user's email address. Must be unique.
        hashed_password (str): The hashed password for the user. Stored as 'password' in the database.
        name (str, optional): The user's name.
        is_active (bool): Flag indicating if the account is active. Defaults to True.
        is_verified (bool): Flag indicating if the account's email has been verified. Defaults to False.
        verified_at (datetime, optional): The timestamp when the email was verified.
        created_at (datetime): Timestamp of when the account was created. Inherited from DateFieldsMixin.
        updated_at (datetime): Timestamp of the last update to the account. Inherited from DateFieldsMixin.
    """
    ormar_config = base_ormar_config.copy(tablename="ACCOUNT")

    id: str = ormar.UUID(primary_key=True, default=uuid4, nullable=False, index=True, uuid_format="string")
    email: str = ormar.String(max_length=255, unique=True, nullable=False, index=True)
    hashed_password: str = ormar.String(max_length=255, nullable=False, name="password")
    name: str = ormar.String(max_length=30, nullable=True)
    is_active: bool = ormar.Boolean(nullable=False, server_default=expression.true(), default=True)
    is_verified: bool = ormar.Boolean(nullable=False, server_default=expression.false(), default=False)
    verified_at: datetime = ormar.DateTime(nullable=True)
