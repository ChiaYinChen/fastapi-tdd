"""Pydantic schemas for authentication operations.

This module defines models for login requests, token responses,
and the structure of token payloads (decoded JWTs).
"""
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Schema for user login requests.

    Requires an email and password for authentication.

    Attributes:
        email (EmailStr): The user's email address.
        password (str): The user's plain text password.
    """
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for representing authentication tokens in API responses.

    Includes the access token, refresh token, and token type.

    Attributes:
        access_token (str): The JWT access token.
        refresh_token (str): The JWT refresh token.
        token_type (str): The type of token (e.g., "bearer").
    """
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Schema for the decoded payload of a JWT.

    Contains standard JWT claims like subject (`sub`), expiration (`exp`),
    and JWT ID (`jti`), along with a custom token `type`.

    Attributes:
        sub (str): The subject of the token (typically the user ID or email).
        type (str): The type of token (e.g., "access", "refresh").
        exp (int): The expiration timestamp of the token (Unix epoch time).
        jti (str): The unique identifier for the token.
    """
    sub: str
    type: str
    exp: int
    jti: str
