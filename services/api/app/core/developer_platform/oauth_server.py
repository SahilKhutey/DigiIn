"""
DigiIn Developer Platform — OAuth 2.0 Authorization Server
Implements client credentials authentication, scoped JWT access token issuance, token introspection, and revocation.
"""

from __future__ import annotations

import hashlib
import secrets
import time
from typing import Any

import jwt

from .models import DeveloperApplication, DeveloperOrganization

JWT_SECRET_KEY = "digiin_oauth_secret_signing_key_production_2026"
JWT_ALGORITHM = "HS256"

# Standard Granular Scopes
VALID_SCOPES = {
    "verification:create",
    "verification:read",
    "verification:education",
    "verification:identity",
    "verification:age",
    "verification:address",
    "proof:verify",
    "proof:read",
    "subject:resolve",
    "webhook:manage",
}

class OAuthAuthorizationServer:
    def __init__(self):
        self._organizations: dict[str, DeveloperOrganization] = {}
        self._applications: dict[str, DeveloperApplication] = {}
        self._clients_by_id: dict[str, DeveloperApplication] = {}
        self._revoked_tokens: set[str] = set()
        self._seed_default_developer_orgs()

    def _seed_default_developer_orgs(self):
        org = self.register_organization(
            name="Delhi Technological University (DTU)",
            org_type="UNIVERSITY"
        )
        self.register_application(
            organization_id=org.id,
            name="DTU Postgraduate Admissions Portal",
            scopes=["verification:create", "verification:read", "verification:education", "proof:verify", "proof:read", "subject:resolve"],
            client_id="dgi_client_dtu_admissions_01",
            raw_secret="dtu_secret_key_8849102"
        )

    def register_organization(self, name: str, org_type: str) -> DeveloperOrganization:
        org_id = f"org_{secrets.token_hex(8)}"
        org = DeveloperOrganization(id=org_id, name=name, type=org_type, status="ACTIVE")
        self._organizations[org_id] = org
        return org

    def register_application(
        self,
        organization_id: str,
        name: str,
        scopes: list[str],
        client_id: str | None = None,
        raw_secret: str | None = None,
        environment: str = "PRODUCTION"
    ) -> tuple[DeveloperApplication, str]:
        c_id = client_id or f"dgi_client_{secrets.token_hex(10)}"
        secret = raw_secret or secrets.token_urlsafe(32)
        secret_hash = hashlib.sha256(secret.encode("utf-8")).hexdigest()

        app_id = f"app_{secrets.token_hex(8)}"
        app = DeveloperApplication(
            id=app_id,
            organization_id=organization_id,
            name=name,
            client_id=c_id,
            client_secret_hash=secret_hash,
            environment=environment,
            status="ACTIVE",
            scopes=scopes
        )
        self._applications[app_id] = app
        self._clients_by_id[c_id] = app
        return app, secret

    def authenticate_client(self, client_id: str, client_secret: str) -> DeveloperApplication | None:
        app = self._clients_by_id.get(client_id)
        if not app or app.status != "ACTIVE":
            return None
        computed_hash = hashlib.sha256(client_secret.encode("utf-8")).hexdigest()
        if secrets.compare_digest(app.client_secret_hash, computed_hash):
            return app
        return None

    def issue_client_credentials_token(
        self,
        client_id: str,
        client_secret: str,
        requested_scopes: list[str] | None = None,
        ttl_seconds: int = 3600
    ) -> tuple[bool, str | None, dict[str, Any] | None]:
        """Issue OAuth 2.0 access token with validated granular scopes."""
        app = self.authenticate_client(client_id, client_secret)
        if not app:
            return False, "INVALID_CLIENT_CREDENTIALS: Authentication failed.", None

        # Scope validation: token scopes cannot exceed application allowed scopes
        allowed = set(app.scopes)
        target_scopes = set(requested_scopes) if requested_scopes else allowed
        unauthorized = target_scopes - allowed
        if unauthorized:
            return False, f"INSUFFICIENT_SCOPE: Requested scope(s) {list(unauthorized)} not granted to application.", None

        now = time.time()
        jti = f"tok_{secrets.token_hex(12)}"
        payload = {
            "iss": "https://api.digiin.in/oauth/v1",
            "sub": app.id,
            "app_id": app.id,
            "client_id": app.client_id,
            "organization_id": app.organization_id,
            "scopes": list(target_scopes),
            "jti": jti,
            "iat": int(now),
            "exp": int(now + ttl_seconds),
        }
        token_str = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return True, None, {
            "access_token": token_str,
            "token_type": "Bearer",
            "expires_in": ttl_seconds,
            "scope": " ".join(target_scopes),
            "jti": jti,
        }

    def introspect_token(self, token_str: str) -> dict[str, Any]:
        """Validate token signature, expiration, and revocation status."""
        try:
            payload = jwt.decode(token_str, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            jti = payload.get("jti")
            if jti in self._revoked_tokens:
                return {"active": False, "reason": "TOKEN_REVOKED"}
            return {
                "active": True,
                "app_id": payload.get("app_id") or payload.get("sub"),
                "client_id": payload.get("client_id"),
                "organization_id": payload.get("organization_id"),
                "scopes": payload.get("scopes", []),
                "exp": payload.get("exp"),
            }
        except jwt.ExpiredSignatureError:
            return {"active": False, "reason": "TOKEN_EXPIRED"}
        except Exception:
            return {"active": False, "reason": "INVALID_TOKEN"}

    def revoke_token(self, token_str: str) -> bool:
        try:
            payload = jwt.decode(token_str, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
            jti = payload.get("jti")
            if jti:
                self._revoked_tokens.add(jti)
                return True
        except Exception:
            pass
        return False
