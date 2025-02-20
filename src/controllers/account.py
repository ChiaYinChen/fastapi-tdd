from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.post(
    "",
    status_code=201,
    summary="Create Account (Register)",
)
async def create_account() -> Any:
    """
    Allow users to sign up and create an account.

    Request Body
    - **email**: user's email (must be unique)
    - **password**: user's password
    """
    pass
