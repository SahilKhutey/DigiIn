from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "DigiLocker X API"
    environment: str = "development"
    database_url: str = "sqlite:///./digilocker_x.db"
    jwt_secret: str = "DEV_ONLY_REPLACE_THIS_SECRET"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    proof_secret: str = "DEV_ONLY_REPLACE_PROOF_SECRET"
    cors_origins: str = "http://localhost:3000"
    redis_url: str = "redis://localhost:6379/0"
    object_storage_bucket: str = "digilocker-x"
    max_upload_mb: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_list(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
