from ..models.account import Account as AccountModel


class AuthService:
    """Service for authentication-related logic."""

    @classmethod
    async def authenticate(cls, email: str, password: str) -> AccountModel | None:
        """Authenticate user by email and password."""
        pass

    @classmethod
    async def create_access_token(cls, sub: str) -> str:
        """Create a short-lived access token."""
        pass

    @classmethod
    async def create_refresh_token(cls, sub: str) -> str:
        """Create a long-lived refresh token."""
        pass
