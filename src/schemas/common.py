from datetime import datetime
from typing import Annotated

from pydantic import Field

DateTimeAnnotation = Annotated[datetime, Field(..., example="2025-02-01T15:30:00")]
