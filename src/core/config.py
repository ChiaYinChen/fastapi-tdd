from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # application
    API_PREFIX: str = "/api"
    POSTGRES_URI: str = "postgresql://root:root@127.0.0.1:5432/dev"

    # testing
    TESTING: bool = False
    TEST_ACCOUNT_EMAIL: EmailStr = "test@example.com"
    TEST_ACCOUNT_PASSWORD: str = "testpass"


settings = Settings()
