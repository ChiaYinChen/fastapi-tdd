from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AccountCreate(BaseModel):
    """Input schema for account creation."""

    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    hashed_password: str = Field(..., min_length=6, alias="password")
    name: str | None = Field(None, max_length=30)
