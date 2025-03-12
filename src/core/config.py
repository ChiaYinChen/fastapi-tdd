from pydantic import EmailStr
from pydantic_settings import BaseSettings

from ..constants.logging import LogLevel


class Settings(BaseSettings):
    # application
    API_PREFIX: str = "/api"
    DOMAIN: str = "http://127.0.0.1:8000"
    DEBUG: bool = False
    LOG_LEVEL: str = LogLevel.INFO
    SECRET_KEY: str = "TEST_SECRET_DO_NOT_USE_IN_PROD"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_TTL: int = 15 * 60  # second
    REFRESH_TOKEN_TTL: int = 60 * 24 * 60  # second

    # postgres
    POSTGRES_URI: str = "postgresql://root:root@postgres:5432/dev"

    # redis
    REDIS_URI: str = "redis://redis:6379"
    BLACK_LIST_REDIS_DB: int = 1

    # smtp
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_SENDER: str = "no-reply@example.com"

    # testing
    TESTING: bool = False
    TEST_ACCOUNT_EMAIL: EmailStr = "test@example.com"
    TEST_ACCOUNT_PASSWORD: str = "testpass"
    TEST_ACCOUNT_NAME: str = "Test User"
    TEST_REDIS_DB: int = 0


settings = Settings()
