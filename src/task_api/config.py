"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the API and database connection."""

    model_config = SettingsConfigDict(env_file=".env.dev", extra="ignore")

    database_url: str = "postgresql+asyncpg://task_api:task_api@localhost:5432/task_api"
    environment: str = "development"
    log_level: str = "INFO"
    default_page_size: int = Field(default=50, ge=1, le=100)
    max_page_size: int = Field(default=100, ge=1, le=500)


@lru_cache
def get_settings() -> Settings:
    """Load and cache runtime settings.

    Returns:
        Settings populated from environment variables and ``.env``.
    """

    return Settings()
