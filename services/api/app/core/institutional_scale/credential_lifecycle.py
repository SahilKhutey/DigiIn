"""
DigiIn Institutional Scale — Multi-Environment Developer Platform & Credential Lifecycle
Manages application environments (SANDBOX, STAGING, PRODUCTION) and zero-downtime credential rotation with grace periods.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field


class AppEnvironment:
    SANDBOX = "SANDBOX"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"

@dataclass
class AppCredential:
    client_id: str
    client_secret_hash: str
    environment: str
    status: str = "ACTIVE"
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    grace_period_until: float | None = None

@dataclass
class DeveloperApplication:
    id: str
    organization_id: str
    name: str
    environment: str = AppEnvironment.SANDBOX
    scopes: list[str] = field(default_factory=list)
    credentials: list[AppCredential] = field(default_factory=list)
    status: str = "ACTIVE"
    created_at: float = field(default_factory=time.time)

class CredentialLifecycleManager:
    def __init__(self):
        self._apps: dict[str, DeveloperApplication] = {}

    def create_application(
        self,
        org_id: str,
        name: str,
        environment: str = AppEnvironment.SANDBOX,
        scopes: list[str] | None = None
    ) -> tuple[DeveloperApplication, str]:
        app_id = f"app_{secrets.token_hex(8)}"
        client_id = f"dgi_cli_{secrets.token_hex(12)}"
        plain_secret = f"dgi_sec_{secrets.token_hex(24)}"
        secret_hash = secrets.token_hex(32)  # Simulated cryptographic hash

        cred = AppCredential(
            client_id=client_id,
            client_secret_hash=secret_hash,
            environment=environment
        )

        app = DeveloperApplication(
            id=app_id,
            organization_id=org_id,
            name=name,
            environment=environment,
            scopes=scopes or ["claims:request", "claims:verify"],
            credentials=[cred]
        )
        self._apps[app_id] = app
        return app, plain_secret

    def rotate_credential(
        self,
        app_id: str,
        grace_period_seconds: int = 86400 * 7
    ) -> tuple[bool, str | None, str | None]:
        app = self._apps.get(app_id)
        if not app or app.status != "ACTIVE":
            return False, None, "APP_NOT_ACTIVE_OR_FOUND"

        # Mark previous credentials for grace-period expiration
        now = time.time()
        for c in app.credentials:
            if c.status == "ACTIVE":
                c.grace_period_until = now + grace_period_seconds

        # Create new primary active credential
        new_client_id = f"dgi_cli_{secrets.token_hex(12)}"
        plain_secret = f"dgi_sec_{secrets.token_hex(24)}"
        secret_hash = secrets.token_hex(32)

        new_cred = AppCredential(
            client_id=new_client_id,
            client_secret_hash=secret_hash,
            environment=app.environment
        )
        app.credentials.append(new_cred)
        return True, plain_secret, None

    def get_application(self, app_id: str) -> DeveloperApplication | None:
        return self._apps.get(app_id)
