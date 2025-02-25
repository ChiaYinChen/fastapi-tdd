from datetime import timedelta

from .. import repositories as crud
from ..core.config import settings
from ..core.security import encode_token, verify_password
from ..models.account import Account as AccountModel


class AuthService:
    """Service for authentication-related logic."""

    @classmethod
    async def authenticate(cls, email: str, password: str) -> AccountModel | None:
        """Authenticate user by email and password."""
        account = await crud.account.get_by_email(email)
        if not account:
            return None
        if not crud.account.is_active(account):
            return None
        if not verify_password(password, account.hashed_password):
            return None
        return account

    @classmethod
    def create_access_token(cls, sub: str) -> str:
        """Create a short-lived access token."""
        return encode_token(
            token_type="access",
            lifetime=timedelta(seconds=settings.ACCESS_TOKEN_TTL),
            sub=sub,
        )

    @classmethod
    def create_refresh_token(cls, sub: str) -> str:
        """Create a long-lived refresh token."""
        return encode_token(
            token_type="refresh",
            lifetime=timedelta(seconds=settings.REFRESH_TOKEN_TTL),
            sub=sub,
        )
