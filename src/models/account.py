from datetime import datetime
from uuid import uuid4

import ormar
from sqlalchemy.sql import expression

from ..db.session import base_ormar_config
from ..models.mixin import DateFieldsMixin


class Account(ormar.Model, DateFieldsMixin):
    """Table for account."""

    ormar_config = base_ormar_config.copy(tablename="ACCOUNT")

    id: str = ormar.UUID(primary_key=True, default=uuid4, nullable=False, index=True, uuid_format="string")
    email: str = ormar.String(max_length=255, unique=True, nullable=False, index=True)
    hashed_password: str = ormar.String(max_length=255, nullable=False, name="password")
    name: str = ormar.String(max_length=30, nullable=True)
    is_active: bool = ormar.Boolean(nullable=False, server_default=expression.true(), default=True)
    is_verified: bool = ormar.Boolean(nullable=False, server_default=expression.false(), default=False)
    verified_at: datetime = ormar.DateTime(nullable=True)
