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

    # Core Phase 1 environment & infrastructure settings
    environment: Environment = "development"
    database_url: str = "sqlite:///./digiin_database.db"
    auth_secret: str | None = None
    object_storage_root: str = "./data/objects"
    max_upload_bytes: int = Field(default=10 * 1024 * 1024, ge=1)
    account_id_prefix: str = "DIN"

    # API and cryptographic token settings
    app_name: str = "DigiLocker X API"
    secret_key: str = "digilocker-x-demo-jwt-secret-key-change-in-production-2026"
    proof_secret: str = "digilocker-x-proof-hmac-sha256-signing-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    cors_list: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    def validate_runtime(self) -> None:
        if self.environment == "production" and not self.auth_secret:
            raise RuntimeError("DIGIIN_AUTH_SECRET is required in production")

    @property
    def is_demo(self) -> bool:
        return self.environment == "demo"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_runtime()
    return settings


# Backwards compatibility instance
settings: Settings = get_settings()
