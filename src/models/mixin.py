"""Provides mixin classes for database models.

This module contains mixins that add common fields or functionality
to Ormar models, such as automatically managed timestamp fields.
"""
from datetime import datetime

import ormar
from sqlalchemy import func


class DateFieldsMixin:
    """A mixin class that adds `created_at` and `updated_at` timestamp fields.

    These fields are automatically managed:
    - `created_at`: Set to the current time when a record is created.
    - `updated_at`: Set to the current time when a record is created and updated
      subsequently (though the `before_update` hook in `src/models/__init__.py`
      is now the primary mechanism for `updated_at` on models using this mixin).

    Attributes:
        created_at (datetime): Timestamp indicating when the record was created.
            Defaults to the current time on record creation.
        updated_at (datetime): Timestamp indicating when the record was last updated.
            Defaults to the current time on creation and is typically updated by
            a pre-update hook.
    """
    created_at: datetime = ormar.DateTime(nullable=False, server_default=func.now(), default=datetime.now)
    updated_at: datetime = ormar.DateTime(
        nullable=False, server_default=func.now(), default=datetime.now, onupdate=datetime.now
    )
