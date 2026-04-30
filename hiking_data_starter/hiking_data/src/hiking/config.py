"""Application configuration loaded from .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Holds API keys loaded from the project root `.env` file."""

    data_go_kr_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Single shared instance — import this from anywhere
settings = Settings()
