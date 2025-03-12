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
    """Generate a hashed password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if the password is correct."""
    return pwd_context.verify(plain_password, hashed_password)


def encode_token(token_type: str, lifetime: timedelta, sub: str) -> str:
    """Generate a JWT token."""
    utc_now = datetime.now(UTC)
    payload = {"type": token_type, "iat": utc_now, "exp": utc_now + lifetime, "sub": str(sub), "jti": str(uuid4())}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    """Decode a JWT token."""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return TokenPayload(**payload)


def encode_url_safe_token(data: dict) -> str:
    """Generate a URL-safe token."""
    return serializer.dumps(data)


def decode_url_safe_token(token: str, max_age: int) -> dict:
    """Decode a URL-safe token."""
    return serializer.loads(token, max_age)
