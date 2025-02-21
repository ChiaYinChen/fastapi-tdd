from datetime import datetime

import ormar
from sqlalchemy import func


class DateFieldsMixin:
    created_at: datetime = ormar.DateTime(nullable=False, server_default=func.now(), default=datetime.now)
    updated_at: datetime = ormar.DateTime(
        nullable=False, server_default=func.now(), default=datetime.now, onupdate=datetime.now
    )
