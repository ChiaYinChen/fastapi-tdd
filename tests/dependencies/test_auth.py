from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from fastapi import Request

from src.dependencies.auth import (
    AccessTokenBearer,
    RefreshTokenBearer,
    RoleChecker,
    TokenBearer,
    blacklist,
    get_account_from_access_token,
    get_account_from_refresh_token,
)
from src.models.account import Account as AccountModel
from src.schemas.auth import TokenPayload
from src.utils.exceptions import NotFoundError, UnauthenticatedError, UnauthorizedError

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


class MockTokenBearer(TokenBearer):
    """Mock TokenBearer for testing."""

    def validate_token_data(self, token_data: TokenPayload) -> bool:
        """Always return True for testing."""
        return True


class InvalidTokenBearer(TokenBearer):
    """Mock to simulate an invalid token bearer."""

    def validate_token_data(self, token_data: TokenPayload) -> bool:
        """Simulate invalid token."""
        return False


@pytest.fixture(scope="module")
def mock_access_token() -> TokenPayload:
    """Mock valid access token."""
    return TokenPayload(sub="test_user@example.com", type="access", exp=9999999999, jti="12345")


@pytest.fixture(scope="module")
def mock_refresh_token() -> TokenPayload:
    """Mock valid refresh token."""
    return TokenPayload(sub="test_user@example.com", type="refresh", exp=9999999999, jti="54321")


@pytest.fixture(scope="module")
def mock_revoked_refresh_token() -> TokenPayload:
    """Mock revoked refresh token."""
    return TokenPayload(sub="test_user@example.com", type="refresh", exp=9999999999, jti="revoked_token")


async def test_token_bearer_with_valid_token(mocker: MockerFixture, mock_access_token: TokenPayload) -> None:
    """Test TokenBearer with valid token."""
    mock_decode = mocker.patch("src.dependencies.auth.decode_token", return_value=mock_access_token)
    request = Request({"type": "http", "headers": [(b"authorization", b"Bearer valid_token")]})
    token_bearer = MockTokenBearer(auto_error=False)
    token_data = await token_bearer(request)

    assert isinstance(token_data, TokenPayload)
    assert token_data.sub == "test_user@example.com"
    mock_decode.assert_called_once_with(token="valid_token")


async def test_token_bearer_with_no_credential() -> None:
    """Test TokenBearer when no credential is provided."""
    request = Request({"type": "http", "headers": []})
    token_bearer = MockTokenBearer(auto_error=False)
    token_data = await token_bearer(request)
    assert token_data is None


async def test_token_bearer_with_invalid_token(mocker: MockerFixture) -> None:
    """Test TokenBearer when invalid token is provided."""
    mocker.patch("src.dependencies.auth.decode_token", side_effect=UnauthenticatedError("errcode", "Invalid token"))
    request = Request({"type": "http", "headers": [(b"authorization", b"Bearer invalid_token")]})
    token_bearer = MockTokenBearer()

    with pytest.raises(UnauthenticatedError):
        await token_bearer(request)


async def test_token_bearer_with_invalid_token_type(mocker: MockerFixture, mock_refresh_token: TokenPayload) -> None:
    """Test TokenBearer if token type is invalid."""
    mocker.patch("src.dependencies.auth.decode_token", return_value=mock_refresh_token)
    request = Request({"type": "http", "headers": [(b"authorization", b"Bearer valid_token")]})
    token_bearer = InvalidTokenBearer()

    with pytest.raises(UnauthenticatedError) as exc_info:
        await token_bearer(request)

    assert exc_info.value.error_code.value == "4004"
    assert exc_info.value.message == "Invalid token type"


async def test_token_bearer_not_implement_validate_token_data(
    mocker: MockerFixture, mock_access_token: TokenPayload
) -> None:
    """Test TokenBearer when validate_token_data is not implemented."""
    mocker.patch("src.dependencies.auth.decode_token", return_value=mock_access_token)
    request = Request({"type": "http", "headers": [(b"authorization", b"Bearer valid_token")]})
    token_bearer = TokenBearer()

    with pytest.raises(NotImplementedError):
        await token_bearer(request)


async def test_access_token_bearer(mocker: MockerFixture, mock_access_token: TokenPayload) -> None:
    """Test AccessTokenBearer with valid token."""
    mocker.patch("src.dependencies.auth.decode_token", return_value=mock_access_token)
    request = Request({"type": "http", "headers": [(b"authorization", b"Bearer valid_token")]})
    access_token_bearer = AccessTokenBearer(auto_error=False)
    token_data = await access_token_bearer(request)

    assert isinstance(token_data, TokenPayload)
    assert token_data.type == "access"


async def test_refresh_token_bearer(mocker: MockerFixture, mock_refresh_token: TokenPayload) -> None:
    """Test RefreshTokenBearer with valid token."""
    mocker.patch("src.dependencies.auth.decode_token", return_value=mock_refresh_token)
    mock_is_token_revoked = mocker.patch(
        "src.dependencies.auth.RefreshTokenBearer.is_token_revoked", return_value=False
    )
    request = Request({"type": "http", "headers": [(b"authorization", b"Bearer valid_token")]})
    refresh_token_bearer = RefreshTokenBearer(auto_error=False)
    token_data = await refresh_token_bearer(request)

    assert isinstance(token_data, TokenPayload)
    assert token_data.type == "refresh"
    mock_is_token_revoked.assert_called_once_with("54321")


async def test_revoked_refresh_token(mocker: MockerFixture, mock_revoked_refresh_token: TokenPayload) -> None:
    """Test RefreshTokenBearer rejects revoked token."""
    mocker.patch("src.dependencies.auth.decode_token", return_value=mock_revoked_refresh_token)
    mock_is_token_revoked = mocker.patch("src.dependencies.auth.RefreshTokenBearer.is_token_revoked", return_value=True)
    request = Request({"type": "http", "headers": [(b"authorization", b"Bearer valid_token")]})
    refresh_token_bearer = RefreshTokenBearer(auto_error=False)

    with pytest.raises(UnauthenticatedError) as exc_info:
        await refresh_token_bearer(request)

    assert exc_info.value.error_code.value == "4005"
    assert exc_info.value.message == "Token revoked"
    mock_is_token_revoked.assert_called_once_with("revoked_token")


async def test_get_account_from_access_token(mocker: MockerFixture, mock_access_token: TokenPayload) -> None:
    """Test get account from access token."""
    mocker.patch(
        "src.repositories.account.account.get_by_email",
        return_value=AccountModel(email="test_user@example.com", hashed_password="valid_password"),
    )
    account = await get_account_from_access_token(mock_access_token)
    assert isinstance(account, AccountModel)
    assert account.email == "test_user@example.com"


async def test_get_account_from_access_token_with_no_credential() -> None:
    """Test get account from access token with no credential."""
    account = await get_account_from_access_token(None)
    assert account is None


async def test_get_account_from_access_token_with_account_not_found(
    mocker: MockerFixture, mock_access_token: TokenPayload
) -> None:
    """Test NotFoundError if account does not exist."""
    mocker.patch("src.repositories.account.account.get_by_email", return_value=None)
    with pytest.raises(NotFoundError) as exc_info:
        await get_account_from_access_token(mock_access_token)
    assert exc_info.value.error_code.value == "1001"
    assert exc_info.value.message == "Account not found"


async def test_get_account_from_refresh_token(mocker: MockerFixture, mock_refresh_token: TokenPayload) -> None:
    """Test get account from refresh token."""
    mocker.patch(
        "src.repositories.account.account.get_by_email",
        return_value=AccountModel(email="test_user@example.com", hashed_password="valid_password"),
    )
    mock_revoke_token = mocker.patch.object(blacklist, "save", return_value=None)
    account = await get_account_from_refresh_token(mock_refresh_token)
    assert isinstance(account, AccountModel)
    assert account.email == "test_user@example.com"
    mock_revoke_token.assert_called_once()


async def test_get_account_from_refresh_token_with_no_credential() -> None:
    """Test get account from refresh token with no credential error."""
    with pytest.raises(UnauthenticatedError) as exc_info:
        await get_account_from_refresh_token(None)
    assert exc_info.value.error_code.value == "4001"
    assert exc_info.value.message == "Not authenticated"


async def test_get_account_from_refresh_token_with_account_not_found(
    mocker: MockerFixture, mock_refresh_token: TokenPayload
) -> None:
    """Test NotFoundError if account does not exist."""
    mock_revoke_token = mocker.patch.object(blacklist, "save", return_value=None)
    mocker.patch("src.repositories.account.account.get_by_email", return_value=None)
    with pytest.raises(NotFoundError) as exc_info:
        await get_account_from_refresh_token(mock_refresh_token)
    assert exc_info.value.error_code.value == "1001"
    assert exc_info.value.message == "Account not found"
    mock_revoke_token.assert_called_once()


def test_role_checker_with_guest_allowed() -> None:
    """Allow guest access if 'GUEST' is in allowed_roles."""
    checker = RoleChecker(["GUEST"])
    result = checker(None)
    assert result is None


def test_role_checker_with_require_authentication() -> None:
    """Raise UnauthenticatedError if authentication is required but no user is provided."""
    checker = RoleChecker(["MEMBER"])
    with pytest.raises(UnauthenticatedError) as exc_info:
        checker(None)
    assert exc_info.value.error_code.value == "4001"
    assert exc_info.value.message == "Not authenticated"


def test_role_checker_with_inactive_account(mocker: MockerFixture) -> None:
    """Raise UnauthorizedError if account is inactive."""
    checker = RoleChecker(["MEMBER"])
    mock_account = AccountModel(email="test_user@example.com", hashed_password="valid_password", is_active=False)
    with pytest.raises(UnauthorizedError) as exc_info:
        checker(mock_account)
    assert exc_info.value.error_code.value == "4007"
    assert exc_info.value.message == "Operation not permitted"


def test_role_checker_success() -> None:
    """Test access for valid user with required role."""
    checker = RoleChecker(["MEMBER"])
    mock_account = AccountModel(email="test_user@example.com", hashed_password="valid_password", is_active=True)
    result = checker(mock_account)
    assert isinstance(result, AccountModel)
    assert result.email == "test_user@example.com"
