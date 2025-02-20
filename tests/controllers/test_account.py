"""Unit tests for account API endpoint."""

from httpx import AsyncClient

from tests.utils.validator import is_valid_time_format


async def test_register_account(client: AsyncClient) -> None:
    """Test response format of `/api/accounts` endpoint for register a new account."""
    data = {"email": "hello@gmail.com", "password": "hellopass"}
    resp = await client.post("/api/accounts", json=data)
    created_account = resp.json()
    assert resp.status_code == 201
    assert isinstance(created_account.get("data"), dict)
    created_account = created_account.get("data")
    assert set(created_account.keys()) == {"email", "name", "is_active", "created_at", "updated_at"}
    assert isinstance(created_account["email"], str)
    assert isinstance(created_account["is_active"], bool)
    assert isinstance(created_account["created_at"], str)
    assert is_valid_time_format(created_account["created_at"])


async def test_register_existing_account(client: AsyncClient) -> None:
    """Test response format of `/api/accounts` endpoint for register an existing account."""
    data = {"email": "hello@gmail.com", "password": "hellopass"}
    resp = await client.post("/api/accounts", json=data)
    created_account = resp.json()
    assert resp.status_code == 409
    assert isinstance(created_account["error_code"], str)
    assert created_account["message"] == "Email already registered"


async def test_password_invalid_length(client: AsyncClient) -> None:
    """Test response of `/api/accounts` endpoint for invalid password length."""
    data = {"email": "admin@gmail.com", "password": "pass"}
    resp = await client.post("/api/accounts", json=data)
    created_account = resp.json()
    assert resp.status_code == 400
    assert isinstance(created_account["error_code"], str)
