"""Unit tests for auth service logic."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import jwt
import pytest

from src import repositories as crud
from src.core.config import settings
from src.core.security import decode_token, encode_token, get_password_hash, verify_password
from src.models.account import Account as AccountModel
from src.schemas.auth import TokenPayload
from src.services.auth import AuthService

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_hash_password() -> None:
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


def test_verify_password() -> None:
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


def test_encode_token() -> None:
    """Test the encoding of a JWT token."""
    token = encode_token(
        token_type="access",
        lifetime=timedelta(minutes=5),
        sub="test_user@example.com",
    )
    assert isinstance(token, str)
    assert len(token.split(".")) == 3  # JWT tokens consist of three parts (header, payload, signature)


def test_decode_token() -> None:
    """Test the decoding of a valid JWT token."""
    token_type = "access"
    lifetime = timedelta(minutes=5)
    sub = "test_user@example.com"
    token = encode_token(token_type, lifetime, sub)
    decoded_data = decode_token(token)
    assert isinstance(decoded_data, TokenPayload)
    assert decoded_data.type == token_type
    assert decoded_data.sub == sub
    assert isinstance(decoded_data.exp, int)

    expected_exp = datetime.now(UTC) + lifetime
    # allow a small buffer (5 seconds) for the expiration time
    assert abs(decoded_data.exp - int(expected_exp.timestamp())) < 5


def test_decode_expired_token() -> None:
    """Test decoding of an expired JWT token."""
    token_type = "access"
    expired_lifetime = timedelta(seconds=-1)  # expire immediately
    sub = "test_user@example.com"
    expired_token = encode_token(token_type, expired_lifetime, sub)
    with pytest.raises(jwt.exceptions.ExpiredSignatureError):
        decode_token(expired_token)


def test_decode_token_with_invalid_signature() -> None:
    """Test decoding of a JWT token with an invalid signature."""
    token_type = "access"
    lifetime = timedelta(minutes=15)
    sub = "test_user@example.com"
    token = encode_token(token_type, lifetime, sub)

    # modify the token to make the signature invalid
    invalid_token = token[:-1]

    with pytest.raises(jwt.exceptions.InvalidSignatureError):
        decode_token(invalid_token)


def test_decode_token_with_invalid_format() -> None:
    """Test decoding of a JWT token with an invalid format."""
    malformed_token = "this.is.not.a.valid.token"

    with pytest.raises(jwt.exceptions.DecodeError):
        decode_token(malformed_token)


async def test_create_access_token(mocker: MockerFixture) -> None:
    """Test that an access token is correctly generated."""
    sub = settings.TEST_ACCOUNT_EMAIL
    lifetime = timedelta(minutes=15)

    mock_encode_token = mocker.patch("src.services.auth.encode_token", return_value="fake_jwt_token")
    token = AuthService.create_access_token(sub)
    mock_encode_token.assert_called_once_with(
        token_type="access",
        lifetime=lifetime,
        sub=sub,
    )
    assert token == "fake_jwt_token"


async def test_create_refresh_token(mocker: MockerFixture) -> None:
    """Test that a refresh token is correctly generated."""
    sub = settings.TEST_ACCOUNT_EMAIL
    lifetime = timedelta(days=1)

    mock_encode_token = mocker.patch("src.services.auth.encode_token", return_value="fake_jwt_token")
    token = AuthService.create_refresh_token(sub)
    mock_encode_token.assert_called_once_with(
        token_type="refresh",
        lifetime=lifetime,
        sub=sub,
    )
    assert token == "fake_jwt_token"
