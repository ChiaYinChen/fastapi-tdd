"""Unit tests for auth service logic."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

from src import repositories as crud
from src.core.config import settings
from src.core.security import get_password_hash, verify_password
from src.models.account import Account as AccountModel
from src.services.auth import AuthService

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_hash_password():
    """
    Test password hashing and verification.
    Ensure that password can be hashed and the hash is verified correctly.
    """
    password = "mysecretpassword"
    hashed_password = get_password_hash(password)
    # verify the hashed password contains the expected algorithm
    assert "$pbkdf2-sha256" in hashed_password
    # verify the hashed password matches the original password
    assert verify_password(password, hashed_password) is True


def test_verify_password():
    """
    Test password verification.
    Verify that the correct password is accepted and the wrong password is rejected.
    """
    plain_password = "wrongpassword"
    hashed_password = get_password_hash("correctpassword")
    # assert wrong password doesn't match the hash
    assert verify_password(plain_password, hashed_password) is False

    correct_password = "correctpassword"
    # assert correct password matches the hash
    assert verify_password(correct_password, hashed_password) is True


async def test_authenticate_with_valid_user(mocker: MockerFixture) -> None:
    """Test authentication with a valid user."""
    mock_account = AccountModel(email=settings.TEST_ACCOUNT_EMAIL, hashed_password=get_password_hash("valid_password"))

    # mock the repository to return a valid user account
    mocker.patch.object(crud.account, "get_by_email", new=AsyncMock(return_value=mock_account))
    mocker.patch.object(crud.account, "is_active", return_value=True)
    # mock password verification to return True (indicating a correct password)
    mocker.patch("src.services.auth.verify_password", return_value=True)

    result = await AuthService.authenticate(email=settings.TEST_ACCOUNT_EMAIL, password="valid_password")
    assert isinstance(result, AccountModel)
    # ensure the result matches the mock account
    assert result is mock_account


async def test_authenticate_with_invalid_email(mocker: MockerFixture) -> None:
    """Test authentication with a non-existent email."""
    # mock the repository to return None (indicating no user found)
    mocker.patch.object(crud.account, "get_by_email", new=AsyncMock(return_value=None))

    result = await AuthService.authenticate(email="not_exists@example.com", password="valid_password")
    assert result is None


async def test_authenticate_with_invalid_password(mocker: MockerFixture) -> None:
    """Test authentication with an incorrect password."""
    mock_account = AccountModel(
        email=settings.TEST_ACCOUNT_EMAIL, hashed_password=get_password_hash(settings.TEST_ACCOUNT_PASSWORD)
    )

    # mock the repository to return a valid user account
    mocker.patch.object(crud.account, "get_by_email", new=AsyncMock(return_value=mock_account))
    mocker.patch.object(crud.account, "is_active", return_value=True)
    # mock password verification to return False (indicating an incorrect password)
    mocker.patch("src.services.auth.verify_password", return_value=False)

    result = await AuthService.authenticate(email=settings.TEST_ACCOUNT_EMAIL, password="invalid_password")
    assert result is None


async def test_authenticate_with_inactive_account(mocker: MockerFixture) -> None:
    """Test authentication with an inactive account."""
    mock_account = AccountModel(email=settings.TEST_ACCOUNT_EMAIL, hashed_password=get_password_hash("valid_password"))

    # mock the repository to return the inactive user account
    mocker.patch.object(crud.account, "get_by_email", new=AsyncMock(return_value=mock_account))
    mocker.patch.object(crud.account, "is_active", return_value=False)

    result = await AuthService.authenticate(email=settings.TEST_ACCOUNT_EMAIL, password="valid_password")
    assert result is None


async def test_create_access_token():
    """Test that an access token is correctly generated and decodable."""
    pass
    # sub = settings.TEST_ACCOUNT_EMAIL
    # token = await AuthService.create_access_token(sub)
    # TODO: jwt decode


async def test_create_refresh_token():
    """Test that a refresh token is correctly generated and decodable."""
    pass
    # sub = settings.TEST_ACCOUNT_EMAIL
    # token = await AuthService.create_refresh_token(sub)
    # TODO: jwt decode
