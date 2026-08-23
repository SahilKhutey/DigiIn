"""
DigiIn Production Infrastructure — Environment Configuration & Isolation
Manages runtime configuration across LOCAL, DEVELOPMENT, STAGING, and PRODUCTION with strict boundary enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass


class EnvironmentType:
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass(frozen=True)
class RuntimeConfig:
    environment: str
    database_url_ref: str
    storage_bucket: str
    api_base_url: str
    kms_key_reference: str
    provider_mode: str  # "sandbox" | "production"
    tls_enforced: bool = True
    allow_synthetic_accounts: bool = False

    def validate_isolation(self):
        """Ensure staging/development never connects to production resources."""
        if self.environment in (EnvironmentType.DEVELOPMENT, EnvironmentType.STAGING):
            if "prod" in self.database_url_ref.lower() or "prod" in self.storage_bucket.lower():
                raise ValueError("ISOLATION_VIOLATION: Non-production environment attempting to bind to production resource reference.")
            if self.provider_mode == "production" and self.environment == EnvironmentType.DEVELOPMENT:
                raise ValueError("ISOLATION_VIOLATION: Development environment cannot run in live production provider mode.")

class EnvironmentManager:
    @staticmethod
    def get_config(env_name: str) -> RuntimeConfig:
        clean_env = env_name.lower()
        if clean_env == EnvironmentType.PRODUCTION:
            cfg = RuntimeConfig(
                environment=EnvironmentType.PRODUCTION,
                database_url_ref="kms://secrets/digiin-prod-db-url",
                storage_bucket="digiin-prod-documents-encrypted",
                api_base_url="https://api.digiin.in",
                kms_key_reference="projects/digiin-prod/locations/asia-south1/keyRings/prod-ring/cryptoKeys/master",
                provider_mode="production",
                tls_enforced=True,
                allow_synthetic_accounts=False
            )
        elif clean_env == EnvironmentType.STAGING:
            cfg = RuntimeConfig(
                environment=EnvironmentType.STAGING,
                database_url_ref="kms://secrets/digiin-staging-db-url",
                storage_bucket="digiin-staging-documents",
                api_base_url="https://staging-api.digiin.in",
                kms_key_reference="projects/digiin-staging/locations/asia-south1/keyRings/stg-ring/cryptoKeys/master",
                provider_mode="sandbox",
                tls_enforced=True,
                allow_synthetic_accounts=True
            )
        else:
            cfg = RuntimeConfig(
                environment=EnvironmentType.DEVELOPMENT,
                database_url_ref="postgresql://digiin:secret@localhost:5432/digiin_dev",
                storage_bucket="digiin-dev-local-bucket",
                api_base_url="http://localhost:8000",
                kms_key_reference="local://key-dev-master",
                provider_mode="sandbox",
                tls_enforced=False,
                allow_synthetic_accounts=True
            )
        cfg.validate_isolation()
        return cfg
