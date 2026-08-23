"""
DigiIn Privacy & Data Governance — Machine-Enforceable Consent Engine
Binds consent to specific subjects, purposes, scopes, and validity windows with instant revocation capabilities.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field


class ConsentStatus:
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"

@dataclass
class ConsentRecord:
    id: str
    subject_id: str
    purpose_code: str
    scope: list[str]
    recipient_id: str
    policy_version: str
    granted_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    revoked_at: float | None = None
    status: str = ConsentStatus.ACTIVE

    def is_valid(self, required_scope: str) -> bool:
        if self.status != ConsentStatus.ACTIVE:
            return False
        if self.expires_at and time.time() > self.expires_at:
            return False
        return required_scope in self.scope or "*" in self.scope

class ConsentPolicyEngine:
    def __init__(self):
        self._consents: dict[str, ConsentRecord] = {}

    def grant_consent(
        self,
        subject_id: str,
        purpose_code: str,
        scope: list[str],
        recipient_id: str,
        ttl_seconds: int = 86400 * 30,  # 30 days
        policy_version: str = "v2.1"
    ) -> ConsentRecord:
        cid = f"cst_{secrets.token_hex(8)}"
        now = time.time()
        record = ConsentRecord(
            id=cid,
            subject_id=subject_id,
            purpose_code=purpose_code,
            scope=scope,
            recipient_id=recipient_id,
            policy_version=policy_version,
            granted_at=now,
            expires_at=now + ttl_seconds,
            status=ConsentStatus.ACTIVE
        )
        self._consents[cid] = record
        return record

    def revoke_consent(self, consent_id: str) -> bool:
        rec = self._consents.get(consent_id)
        if not rec or rec.status != ConsentStatus.ACTIVE:
            return False
        rec.status = ConsentStatus.REVOKED
        rec.revoked_at = time.time()
        return True

    def evaluate_access(
        self,
        subject_id: str,
        recipient_id: str,
        purpose_code: str,
        requested_scope: str
    ) -> tuple[bool, str | None, ConsentRecord | None]:
        """Evaluate if access is permitted under active, unrevoked, matching consent."""
        matching = [
            c for c in self._consents.values()
            if c.subject_id == subject_id
            and (c.recipient_id == recipient_id or c.recipient_id == "*")
            and c.purpose_code == purpose_code
        ]

        if not matching:
            return False, "NO_MATCHING_CONSENT_FOUND", None

        # Check latest consent
        latest = matching[-1]
        if latest.status == ConsentStatus.REVOKED:
            return False, "CONSENT_EXPLICITLY_REVOKED", latest
        if latest.expires_at and time.time() > latest.expires_at:
            latest.status = ConsentStatus.EXPIRED
            return False, "CONSENT_EXPIRED", latest
        if not latest.is_valid(requested_scope):
            return False, f"SCOPE_UNAUTHORIZED: Scope '{requested_scope}' not granted in consent.", latest

        return True, None, latest
