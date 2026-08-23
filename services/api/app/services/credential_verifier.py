from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.credential_models import Credential, CredentialStatus


def _to_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


class CredentialVerifier:
    """Independent verification of credential state.

    Cryptographic signature verification can be layered on top of this
    state/policy verification without changing the public result shape.
    """

    def verify(self, credential: Credential) -> dict[str, Any]:
        now = datetime.now(UTC)

        if credential.status is CredentialStatus.REVOKED:
            return {"valid": False, "reason": "revoked"}

        if credential.status is CredentialStatus.SUSPENDED:
            return {"valid": False, "reason": "suspended"}

        if credential.expires_at:
            exp_utc = _to_utc(credential.expires_at)
            if exp_utc and exp_utc <= now:
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
