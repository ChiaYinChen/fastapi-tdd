"""Security-related utility functions.

This module provides functions for password hashing and verification,
JWT token encoding and decoding, and URL-safe token generation and validation.
It utilizes `passlib` for password context and `itsdangerous` for timed,
URL-safe serialization, along with `PyJWT` for JWT operations.

Attributes:
    pwd_context (CryptContext): Passlib context for password hashing using pbkdf2_sha256.
    serializer (URLSafeTimedSerializer): itsdangerous serializer for generating
        and validating timed tokens, using the application's SECRET_KEY.
"""
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext

from ..core.config import settings
from ..schemas.auth import TokenPayload

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
serializer = URLSafeTimedSerializer(secret_key=settings.SECRET_KEY)


def get_password_hash(password: str) -> str:
    """Generate a hashed password.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if the password is correct.

    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def encode_token(token_type: str, lifetime: timedelta, sub: str) -> str:
    """Generate a JWT token.

    Args:
        token_type (str): The type of the token (e.g., "access", "refresh").
        lifetime (timedelta): The lifespan of the token.
        sub (str): The subject of the token (e.g., user ID).

    Returns:
        str: The encoded JWT token.
    """
    utc_now = datetime.now(UTC)
    payload = {"type": token_type, "iat": utc_now, "exp": utc_now + lifetime, "sub": str(sub), "jti": str(uuid4())}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    """Decode a JWT token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        TokenPayload: The decoded token payload.

    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is invalid.
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return TokenPayload(**payload)


def encode_url_safe_token(data: dict) -> str:
    """Generate a URL-safe token.

    This token is timed and signed, suitable for use in URLs (e.g., email verification).

    Args:
        data (dict): The data to encode into the token.

    Returns:
        str: The URL-safe, timed, signed token.
    """
    return serializer.dumps(data)


def decode_url_safe_token(token: str, max_age: int) -> dict:
    """Decode a URL-safe token.

    Validates the token's signature and timing.

    Args:
        token (str): The URL-safe token to decode.
        max_age (int): The maximum age of the token in seconds.

    Returns:
        dict: The decoded data from the token.

    Raises:
        itsdangerous.SignatureExpired: If the token has expired.
        itsdangerous.BadTimeSignature: If the token signature is invalid or malformed.
        itsdangerous.BadSignature: If the token signature is invalid.
    """
    return serializer.loads(token, max_age)
