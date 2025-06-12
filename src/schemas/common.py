"""Common Pydantic schemas and type annotations used across the application.

This module defines shared Pydantic models or type aliases that are broadly
applicable to various parts of the schema definitions.

Attributes:
    DateTimeAnnotation (Annotated[datetime, Field]): A type annotation for datetime fields,
        providing an example format for documentation purposes.
"""
from datetime import datetime
from typing import Annotated

from pydantic import Field

DateTimeAnnotation = Annotated[datetime, Field(..., example="2025-02-01T15:30:00")]
