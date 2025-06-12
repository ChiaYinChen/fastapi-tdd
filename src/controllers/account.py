"""API routes for account management.

This module defines FastAPI routes for account creation (registration),
email verification, and password reset operations. It utilizes services
from `AccountService` to handle the business logic.

Attributes:
    router (APIRouter): FastAPI router for account-related endpoints.
    registration_email (AccountVerificationEmail): Email generator for registration.
    email_sender (EmailSender): Email sender configured with `registration_email`.
"""
from typing import Any

from fastapi import APIRouter, Response, status

from ..constants.errors import CustomErrorCode
from ..core.security import verify_password
from ..dependencies.auth import AuthenticatedMember
from ..schemas.account import Account, AccountCreate, ResetPassword
from ..schemas.response import GenericResponse
from ..services.account import AccountService
from ..utils import exceptions as exc
from ..utils.mails import AccountVerificationEmail, EmailSender

router = APIRouter()
registration_email = AccountVerificationEmail()
email_sender = EmailSender(registration_email)


@router.post(
    "",
    response_model=GenericResponse[Account],
    status_code=status.HTTP_201_CREATED,
    summary="Create Account (Register)",
    description="Allows users to sign up and create a new account. An email verification will be sent.",
)
async def create_account(account_in: AccountCreate) -> GenericResponse[Account]:
    """Creates a new user account.

    Args:
        account_in (AccountCreate): The account creation data, including email,
            password, and optional name.

    Returns:
        GenericResponse[Account]: A generic response containing the created account data.

    Raises:
        exc.ConflictError: If an account with the provided email already exists.
    """
    account_obj = await AccountService.get_account_by_email(account_in.email)
    if account_obj:
        raise exc.ConflictError(CustomErrorCode.ENTITY_CONFLICT, "Email already registered")
    account = await AccountService.create_account_without_auth(account_in)
    await email_sender.send(
        recipients=[account.email],
        email=account.email,
        username=account.name,
    )
    return GenericResponse(data=account)


@router.get(
    "/email-verification",
    response_model=GenericResponse[None],
    summary="Confirm Email Verification",
    description="Verifies a user's email address using a provided token.",
)
async def confirm_email_verification(token: str) -> GenericResponse[None]:
    """Confirms a user's email address using a verification token.

    Args:
        token (str): The email verification token received by the user.

    Returns:
        GenericResponse[None]: A generic response indicating successful verification.

    Raises:
        itsdangerous.SignatureExpired: If the token has expired.
        itsdangerous.BadTimeSignature: If the token signature is invalid.
        exc.NotFoundError: If the account associated with the token is not found.
    """
    await AccountService.verify_account(token)
    return GenericResponse(message="Account verified successfully")


@router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reset User Password",
    description="Allows an authenticated user to reset their password.",
)
async def reset_password(current_user: AuthenticatedMember, pwd_in: ResetPassword) -> Response:
    """Resets the authenticated user's password.

    Args:
        current_user (AuthenticatedMember): The authenticated user object (dependency).
        pwd_in (ResetPassword): The password reset data, containing the current
            and new passwords.

    Returns:
        Response: An HTTP 204 No Content response upon successful password reset.

    Raises:
        exc.BadRequestError: If the provided current password is incorrect.
    """
    if not verify_password(pwd_in.current_password, current_user.hashed_password):
        raise exc.BadRequestError(CustomErrorCode.RESET_PASSWORD_MISMATCH, "Incorrect password")
    await AccountService.reset_password(account_obj=current_user, pwd_in=pwd_in)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
