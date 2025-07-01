from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="RESCUE_API_", env_file_encoding="utf-8"
    )

    app_name: str = "Rescue API"
    version: str = "0.0.1"
    postgres_host: str = "db"
    postgres_user: str
    postgres_password: str
    postgres_db: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
