"""Service layer for authentication-related business logic.

This module provides the `AuthService` class, which encapsulates
core authentication functionalities such as user authentication via
email/password and the creation of access and refresh tokens.
"""
from datetime import timedelta

from .. import repositories as crud
from ..core.config import settings
from ..core.security import encode_token, verify_password
from ..models.account import Account as AccountModel


class AuthService:
    """Provides business logic services for user authentication."""

    @classmethod
    async def authenticate(cls, email: str, password: str) -> AccountModel | None:
        """Authenticates a user based on email and password.

        Retrieves the user by email, checks if the account is active,
        and verifies the provided password against the stored hash.

        Args:
            email (str): The user's email address.
            password (str): The user's plain text password.

        Returns:
            AccountModel | None: The authenticated account model if successful,
                otherwise None.
        """
        account = await crud.account.get_by_email(email)
        if not account:
            return None
        if not crud.account.is_active(account): # Or handle with specific exception
            return None
        if not verify_password(password, account.hashed_password):
            return None
        return account

    @classmethod
    def create_access_token(cls, sub: str) -> str:
        """Creates a new JWT access token.

        Access tokens are typically short-lived and used to authenticate
        requests to protected API endpoints.

        Args:
            sub (str): The subject of the token (e.g., user ID or email).

        Returns:
            str: The encoded JWT access token.
        """
        return encode_token(
            token_type="access",
            lifetime=timedelta(seconds=settings.ACCESS_TOKEN_TTL),
            sub=sub,
        )

    @classmethod
    def create_refresh_token(cls, sub: str) -> str:
        """Creates a new JWT refresh token.

        Refresh tokens are typically long-lived and used to obtain new
        access tokens without requiring the user to re-enter credentials.

        Args:
            sub (str): The subject of the token (e.g., user ID or email).

        Returns:
            str: The encoded JWT refresh token.
        """
        return encode_token(
            token_type="refresh",
            lifetime=timedelta(seconds=settings.REFRESH_TOKEN_TTL),
            sub=sub,
        )
