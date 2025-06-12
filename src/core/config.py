from pydantic import EmailStr
from pydantic_settings import BaseSettings

from ..constants.logging import LogLevel


class Settings(BaseSettings):
    """Global application settings.

    These settings are loaded from environment variables or default values
    and are accessible via the `settings` instance.

    Attributes:
        API_PREFIX (str): The prefix for all API routes.
        DOMAIN (str): The domain where the application is hosted.
        DEBUG (bool): Whether the application is in debug mode.
        LOG_LEVEL (str): The logging level for the application.
        SECRET_KEY (str): A secret key for cryptographic operations.
        ALGORITHM (str): The algorithm used for JWT encoding/decoding.
        ACCESS_TOKEN_TTL (int): Time-to-live for access tokens in seconds.
        REFRESH_TOKEN_TTL (int): Time-to-live for refresh tokens in seconds.
        URL_SAFE_TOKEN_TTL (int): Time-to-live for URL-safe tokens (e.g., for email verification) in seconds.
        POSTGRES_URI (str): The connection URI for the PostgreSQL database.
        REDIS_URI (str): The connection URI for Redis.
        BLACK_LIST_REDIS_DB (int): The Redis database number used for token blacklisting.
        MAIL_SERVER (str): The SMTP server address for sending emails.
        MAIL_PORT (int): The SMTP server port.
        MAIL_USERNAME (str): The username for SMTP authentication.
        MAIL_PASSWORD (str): The password for SMTP authentication.
        MAIL_SENDER (str): The default sender email address for application emails.
        TESTING (bool): Whether the application is in testing mode.
        TEST_ACCOUNT_EMAIL (EmailStr): Default email for the test account.
        TEST_ACCOUNT_PASSWORD (str): Default password for the test account.
        TEST_ACCOUNT_NAME (str): Default name for the test account.
        TEST_REDIS_DB (int): The Redis database number used for testing.
    """
    # application
    API_PREFIX: str = "/api"
    DOMAIN: str = "http://127.0.0.1:8000"
    DEBUG: bool = False
    LOG_LEVEL: str = LogLevel.INFO
    SECRET_KEY: str = "TEST_SECRET_DO_NOT_USE_IN_PROD"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_TTL: int = 15 * 60  # second (15 mins)
    REFRESH_TOKEN_TTL: int = 60 * 24 * 60  # second (1 day)
    URL_SAFE_TOKEN_TTL: int = 60 * 60  # second (1 hour)

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
