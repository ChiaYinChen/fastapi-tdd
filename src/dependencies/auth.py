"""Authentication and authorization dependencies for FastAPI.

This module provides classes and functions to handle token-based authentication
(HTTP Bearer for access and refresh tokens) and role-based authorization.
It defines token validation logic, user retrieval from tokens, and role checking
mechanisms for protecting API endpoints.

Attributes:
    blacklist (TokenBlackList): An instance of TokenBlackList used for managing
        revoked refresh tokens.
    AuthenticatedMember (TypeAlias): An Annotated dependency that provides
        an authenticated account model if the user has the "MEMBER" role,
        otherwise raises appropriate HTTP exceptions.
"""
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .. import repositories as crud
from ..constants.errors import CustomErrorCode
from ..core.config import settings
from ..core.security import decode_token
from ..models.account import Account as AccountModel
from ..schemas.auth import TokenPayload
from ..utils import exceptions as exc
from ..utils.blacklist import TokenBlackList

blacklist = TokenBlackList(db=settings.BLACK_LIST_REDIS_DB)


class TokenBearer(HTTPBearer):
    """Handles token authentication using HTTP Bearer tokens.

    This class serves as a base for specific token type bearers, providing
    common token retrieval and initial validation logic.

    Attributes:
        auto_error (bool): If True, automatically raises HTTPException for errors.
    """

    def __init__(self, auto_error: bool = True):
        """Initializes the TokenBearer.

        Args:
            auto_error (bool): If True (default), an HTTPException will be raised
                if the Authorization header is missing or malformed. If False,
                None will be returned in such cases.
        """
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> TokenPayload | None:
        """Validates and decodes the token from the request's Authorization header.

        Retrieves the bearer token, decodes it, and performs initial validation
        based on the `validate_token_data` method implemented by subclasses.

        Args:
            request (Request): The incoming FastAPI request.

        Returns:
            TokenPayload | None: The decoded token payload if valid, otherwise None
                if `auto_error` is False and no token is present.

        Raises:
            exc.UnauthenticatedError: If the token type is invalid (raised by `validate_token_data`).
            HTTPException: If `auto_error` is True and token is missing/malformed (from `HTTPBearer`).
        """
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(request)
        if not credentials:
            return None
        token_data = decode_token(token=credentials.credentials)
        if not self.validate_token_data(token_data):
            raise exc.UnauthenticatedError(CustomErrorCode.INVALID_TOKEN_TYPE, "Invalid token type")
        return token_data

    def validate_token_data(self, token_data: TokenPayload) -> bool:
        """Validates the specific type or properties of the token data.

        This method must be implemented by subclasses to define how a specific
        token type (e.g., access, refresh) should be validated.

        Args:
            token_data (TokenPayload): The decoded token payload.

        Returns:
            bool: True if the token data is valid for the expected type, False otherwise.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement this method")


class AccessTokenBearer(TokenBearer):
    """Handles access token validation by ensuring the token type is 'access'."""

    def validate_token_data(self, token_data: TokenPayload) -> bool:
        """Checks if the token is an access token.

        Args:
            token_data (TokenPayload): The decoded token payload.

        Returns:
            bool: True if the token type is 'access', False otherwise.
        """
        return True if token_data.type == "access" else False


class RefreshTokenBearer(TokenBearer):
    """Handles refresh token validation.

    Ensures the token type is 'refresh' and checks if the token has been revoked
    by consulting the token blacklist.
    """

    def validate_token_data(self, token_data: TokenPayload) -> bool:
        """Checks if the token is a valid, non-revoked refresh token.

        Args:
            token_data (TokenPayload): The decoded token payload.

        Returns:
            bool: True if the token is a valid 'refresh' token and not revoked.

        Raises:
            exc.UnauthenticatedError: If the token has been revoked.
        """
        if token_data.type != "refresh":
            return False
        if self.is_token_revoked(token_data.jti):
            raise exc.UnauthenticatedError(CustomErrorCode.TOKEN_REVOKED, "Token revoked")
        return True

    def is_token_revoked(self, jti: str) -> bool:
        """Checks if the token (by its JTI) has been revoked.

        Args:
            jti (str): The JWT ID (jti) of the token.

        Returns:
            bool: True if the token is found in the blacklist (revoked), False otherwise.
        """
        return True if blacklist.get(token=jti) else False


async def get_account_from_access_token(
    token_data: TokenPayload | None = Depends(AccessTokenBearer(auto_error=False)),
) -> AccountModel | None:
    """Retrieves an account using an access token's payload.

    This dependency attempts to fetch an account based on the subject ('sub')
    field of a validated access token. If the token is not provided or invalid,
    it returns None.

    Args:
        token_data (TokenPayload | None): The decoded access token payload,
            obtained from `AccessTokenBearer`. Defaults to Depends(...).

    Returns:
        AccountModel | None: The authenticated account if found and token is valid,
            otherwise None.

    Raises:
        exc.NotFoundError: If the account specified in the token is not found.
    """
    if not token_data:
        return None
    account = await crud.account.get_by_email(email=token_data.sub)
    if not account:
        raise exc.NotFoundError(CustomErrorCode.ENTITY_NOT_FOUND, "Account not found")
    return account


async def get_account_from_refresh_token(
    token_data: TokenPayload | None = Depends(RefreshTokenBearer(auto_error=False)),
) -> AccountModel:
    """Retrieves an account using a refresh token's payload.

    This dependency requires a valid refresh token. It blacklists the used
    refresh token (by its JTI) and then fetches the account.

    Args:
        token_data (TokenPayload | None): The decoded refresh token payload,
            obtained from `RefreshTokenBearer`. Defaults to Depends(...).

    Returns:
        AccountModel: The authenticated account.

    Raises:
        exc.UnauthenticatedError: If no token data is provided (token is missing or invalid).
        exc.NotFoundError: If the account specified in the token is not found.
    """
    if not token_data:
        raise exc.UnauthenticatedError(CustomErrorCode.NOT_AUTHENTICATED, "Not authenticated")
    blacklist.save(token=token_data.jti, ttl=settings.REFRESH_TOKEN_TTL)
    account = await crud.account.get_by_email(email=token_data.sub)
    if not account:
        raise exc.NotFoundError(CustomErrorCode.ENTITY_NOT_FOUND, "Account not found")
    return account


class RoleChecker:
    """Dependency class to check user roles and permissions.

    This class is used as a FastAPI dependency to protect routes by ensuring
    the authenticated user has one of the allowed roles.

    Attributes:
        allowed_roles (list[str]): A list of role names that are permitted
            to access the resource.
    """

    def __init__(self, allowed_roles: list[str]):
        """Initializes the RoleChecker.

        Args:
            allowed_roles (list[str]): A list of role names that are permitted.
        """
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: AccountModel | None = Depends(get_account_from_access_token)) -> AccountModel | None:
        """Checks if the current user has the required role.

        - If "GUEST" is in `allowed_roles`, access is granted even without a user.
        - If authentication is required (not "GUEST") and no user is present,
          an UnauthenticatedError is raised.
        - If the user is present, checks if their account is active.
        - TODO: Implement actual role string comparison once roles are on AccountModel.

        Args:
            current_user (AccountModel | None): The authenticated user account,
                obtained from `get_account_from_access_token`. Defaults to Depends(...).

        Returns:
            AccountModel | None: The current user if authorized, or None if "GUEST"
                is allowed and no user is present.

        Raises:
            exc.UnauthenticatedError: If authentication is required and no user is present.
            exc.UnauthorizedError: If the user's account is inactive or (future)
                if the user does not possess any of the allowed roles.
        """
        # require authentication unless 'GUEST' access is allowed
        if "GUEST" not in self.allowed_roles and not current_user:
            raise exc.UnauthenticatedError(CustomErrorCode.NOT_AUTHENTICATED, "Not authenticated")
        # check if user has the required authorization
        # TODO: implement role-based permission checking logic
        if current_user:
            if not crud.account.is_active(current_user):
                raise exc.UnauthorizedError(CustomErrorCode.OPERATION_NOT_PERMITTED, "Operation not permitted")
            return current_user
        # allow guest access
        return None


AuthenticatedMember = Annotated[AccountModel | None, Depends(RoleChecker(["MEMBER"]))]
