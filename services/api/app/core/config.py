import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    app_name: str = "DigiLocker X API"
    secret_key: str = "digilocker-x-demo-jwt-secret-key-change-in-production-2026"
    proof_secret: str = "digilocker-x-proof-hmac-sha256-signing-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    database_url: str = os.getenv("DIGIIN_DATABASE_URL", "sqlite:///./digiin_database.db")
    cors_list: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]


settings = Settings()
