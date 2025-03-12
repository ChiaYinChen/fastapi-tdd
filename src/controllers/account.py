from typing import Any

from fastapi import APIRouter, status

from ..constants.errors import CustomErrorCode
from ..schemas.account import Account, AccountCreate
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
