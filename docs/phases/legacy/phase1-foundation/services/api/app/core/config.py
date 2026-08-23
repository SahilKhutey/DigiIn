from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


Environment = Literal["demo", "development", "test", "production"]


class Settings(BaseSettings):
    """Explicit runtime configuration for the DigiIn API.

    Production deliberately requires externally supplied secrets rather than
    silently falling back to development/demo values.
    """

    model_config = SettingsConfigDict(
        env_prefix="DIGIIN_",
        env_file=".env",
        extra="ignore",
    )

    environment: Environment = "development"
    database_url: str = "sqlite:///./digiin_database.db"
    auth_secret: str | None = None
    object_storage_root: str = "./data/objects"
    max_upload_bytes: int = Field(default=10 * 1024 * 1024, ge=1)
    account_id_prefix: str = "DIN"

    def validate_runtime(self) -> None:
        if self.environment == "production" and not self.auth_secret:
            raise RuntimeError("DIGIIN_AUTH_SECRET is required in production")

    @property
    def is_demo(self) -> bool:
        return self.environment == "demo"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_runtime()
    return settings
