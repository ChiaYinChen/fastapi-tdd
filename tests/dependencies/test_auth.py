from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from src.dependencies.auth import RoleChecker, get_account_from_token
from src.models.account import Account as AccountModel
from src.schemas.auth import TokenPayload
from src.utils.exceptions import NotFoundError, UnauthenticatedError, UnauthorizedError

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


async def test_get_account_from_token_with_no_credential():
    """Return None if no credential is provided.."""
    account = await get_account_from_token(None)
    assert account is None


async def test_get_account_from_token_with_invalid_token(mocker: MockerFixture) -> None:
    """Raise UnauthenticatedError if token is invalid."""
    mocker.patch("src.dependencies.auth.decode_token", side_effect=UnauthenticatedError("errcode", "Invalid token"))
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
    with pytest.raises(UnauthenticatedError):
        await get_account_from_token(credentials)


async def test_get_account_from_token_with_invalid_token_type(mocker: MockerFixture):
    """Raise UnauthenticatedError if token type is not `access`."""
    mocker.patch(
        "src.dependencies.auth.decode_token",
        return_value=TokenPayload(type="refresh", sub="test_user@example.com", exp=9999999999),
    )
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
    with pytest.raises(UnauthenticatedError) as exc_info:
        await get_account_from_token(credentials)
    assert exc_info.value.error_code.value == "4004"
    assert exc_info.value.message == "Invalid token type"


async def test_get_account_from_token_with_account_not_found(mocker: MockerFixture):
    """Raise NotFoundError if account does not exist."""
    mocker.patch(
        "src.dependencies.auth.decode_token",
        return_value=TokenPayload(type="access", sub="test_user@example.com", exp=9999999999),
    )
    mocker.patch("src.repositories.account.account.get_by_email", return_value=None)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
    with pytest.raises(NotFoundError) as exc_info:
        await get_account_from_token(credentials)
    assert exc_info.value.error_code.value == "1001"
    assert exc_info.value.message == "Account not found"


async def test_get_account_from_token_success(mocker: MockerFixture):
    """Return the account if everything is valid."""
    mocker.patch(
        "src.dependencies.auth.decode_token",
        return_value=TokenPayload(type="access", sub="test_user@example.com", exp=9999999999),
    )
    mocker.patch(
        "src.repositories.account.account.get_by_email",
        return_value=AccountModel(email="test_user@example.com", hashed_password="valid_password"),
    )
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
    account = await get_account_from_token(credentials)
    assert account is not None
    assert account.email == "test_user@example.com"


def test_role_checker_with_guest_allowed():
    """Allow guest access if 'GUEST' is in allowed_roles."""
    checker = RoleChecker(["GUEST"])
    result = checker(None)
    assert result is None


def test_role_checker_with_require_authentication():
    """Raise UnauthenticatedError if authentication is required but no user is provided."""
    checker = RoleChecker(["MEMBER"])
    with pytest.raises(UnauthenticatedError) as exc_info:
        checker(None)
    assert exc_info.value.error_code.value == "4001"
    assert exc_info.value.message == "Not authenticated"


def test_role_checker_with_inactive_account(mocker: MockerFixture):
    """Raise UnauthorizedError if account is inactive."""
    checker = RoleChecker(["MEMBER"])
    mock_account = AccountModel(email="test_user@example.com", hashed_password="valid_password", is_active=False)
    with pytest.raises(UnauthorizedError) as exc_info:
        checker(mock_account)
    assert exc_info.value.error_code.value == "4007"
    assert exc_info.value.message == "Operation not permitted"


def test_role_checker_success():
    """Test access for valid user with required role."""
    checker = RoleChecker(["MEMBER"])
    mock_account = AccountModel(email="test_user@example.com", hashed_password="valid_password", is_active=True)
    result = checker(mock_account)
    assert isinstance(result, AccountModel)
    assert result.email == "test_user@example.com"
