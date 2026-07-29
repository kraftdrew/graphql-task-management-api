"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the API and database connection."""

    model_config = SettingsConfigDict(env_file=".env.dev", extra="ignore")

    database_url: str = "postgresql+asyncpg://task_api:task_api@localhost:5432/task_api"


@lru_cache
def get_settings() -> Settings:
    """Load and cache runtime settings.

    Returns:
        Settings populated from environment variables and ``.env.dev``.
    """

    return Settings()
