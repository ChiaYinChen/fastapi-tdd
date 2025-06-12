"""API routes for user authentication.

This module defines FastAPI routes for user login and token refresh operations.
It utilizes `AuthService` for the core authentication logic and token generation.

Attributes:
    router (APIRouter): FastAPI router for authentication-related endpoints.
"""
from __future__ import annotations # Corrected this line
from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, Depends, status

from ..constants.errors import CustomErrorCode
from ..dependencies.auth import get_account_from_refresh_token
from ..schemas.auth import LoginRequest, Token
from ..schemas.response import GenericResponse
from ..services.auth import AuthService
from ..utils import exceptions as exc

if TYPE_CHECKING:
    from ..models.account import Account as AccountModel

router = APIRouter()


@router.post(
    "/login",
    response_model=GenericResponse[Token],
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and generate tokens",
    description=(
        "Authenticates a user via email and password, then generates and returns "
        "access and refresh tokens. Access tokens expire in 15 minutes, "
        "refresh tokens expire in 24 hours."
    ),
)
async def login(login_data: LoginRequest) -> GenericResponse[Token]:
    """Authenticates a user and provides access and refresh tokens.

    Args:
        login_data (LoginRequest): The login credentials (email and password).

    Returns:
        GenericResponse[Token]: A generic response containing the access token,
            refresh token, and token type ("bearer").

    Raises:
        exc.UnauthenticatedError: If authentication fails due to incorrect
            email or password.
    """
    account = await AuthService.authenticate(email=login_data.email, password=login_data.password)
    if not account:
        raise exc.UnauthenticatedError(CustomErrorCode.INCORRECT_EMAIL_OR_PASSWORD, "Incorrect email or password")
    return GenericResponse(
        data=Token(
            access_token=AuthService.create_access_token(sub=account.email),
            refresh_token=AuthService.create_refresh_token(sub=account.email),
            token_type="bearer",
        )
    )


@router.post(
    "/refresh-token",
    response_model=GenericResponse[Token],
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description="Renews the user's access token using a valid refresh token.",
)
async def refresh_token(current_user: AccountModel = Depends(get_account_from_refresh_token)) -> GenericResponse[Token]:
    """Renews a user's access and refresh tokens using a valid refresh token.

    The refresh token itself is also renewed (rotated) as part of this process.

    Args:
        current_user (AccountModel): The user account associated with the valid
            refresh token (dependency).

    Returns:
        GenericResponse[Token]: A generic response containing a new access token,
            a new refresh token, and the token type ("bearer").
    """
    return GenericResponse(
        data=Token(
            access_token=AuthService.create_access_token(sub=current_user.email),
            refresh_token=AuthService.create_refresh_token(sub=current_user.email),
            token_type="bearer",
        )
    )
