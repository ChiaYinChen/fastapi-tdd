from pydantic import EmailStr
from pydantic_settings import BaseSettings

from ..constants.logging import LogLevel


class Settings(BaseSettings):
    # application
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    LOG_LEVEL: str = LogLevel.INFO
    POSTGRES_URI: str = "postgresql://root:root@postgres:5432/dev"

    # testing
    TESTING: bool = False
    TEST_ACCOUNT_EMAIL: EmailStr = "test@example.com"
    TEST_ACCOUNT_PASSWORD: str = "testpass"
    TEST_ACCOUNT_NAME: str = "Test User"


settings = Settings()
