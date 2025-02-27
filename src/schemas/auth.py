from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Input schema for login request."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Token payload."""

    sub: str
    type: str
    exp: int
    jti: str
