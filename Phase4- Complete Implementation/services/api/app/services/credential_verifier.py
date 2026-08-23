from __future__ import annotations

from datetime import datetime, timezone

from app.domain.credential_models import Credential, CredentialStatus


class CredentialVerifier:
    """Independent verification of credential state.

    Cryptographic signature verification can be layered on top of this
    state/policy verification without changing the public result shape.
    """

    def verify(self, credential: Credential) -> dict:
        now = datetime.now(timezone.utc)

        if credential.status is CredentialStatus.REVOKED:
            return {"valid": False, "reason": "revoked"}

        if credential.status is CredentialStatus.SUSPENDED:
            return {"valid": False, "reason": "suspended"}

        if credential.expires_at and credential.expires_at <= now:
            return {"valid": False, "reason": "expired"}

        return {
            "valid": credential.status is CredentialStatus.ACTIVE,
            "reason": "active",
            "credential_id": credential.credential_id,
            "credential_type": credential.credential_type,
            "issuer": credential.issuer,
            "issued_at": credential.issued_at,
            "expires_at": credential.expires_at,
        }
