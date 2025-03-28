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
)
async def create_account(account_in: AccountCreate) -> Any:
    """
    Allow users to sign up and create an account.
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
)
async def confirm_email_verification(token: str) -> Any:
    """
    Verify a user's email to confirm registration.
    """
    await AccountService.verify_account(token)
    return GenericResponse(message="Account verified successfully")


@router.post(
    "/reset-password",
)
async def reset_password(current_user: AuthenticatedMember, pwd_in: ResetPassword) -> Any:
    """
    Reset user's password.
    """
    if not verify_password(pwd_in.current_password, current_user.hashed_password):
        raise exc.BadRequestError(CustomErrorCode.RESET_PASSWORD_MISMATCH, "Incorrect password")
    await AccountService.reset_password(account_obj=current_user, pwd_in=pwd_in)
    return Response(status_code=204)
