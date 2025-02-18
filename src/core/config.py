"""Settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # application
    API_PREFIX: str = "/api"


settings = Settings()
