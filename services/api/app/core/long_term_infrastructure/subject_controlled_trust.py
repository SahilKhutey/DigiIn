"""
DigiIn Long-Term Infrastructure — Subject-Controlled Trust & Consent Layer
Empowers citizens to manage active permissions, time-bounded sharing windows, and instant consent revocation.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field


@dataclass
class CitizenConsentGrant:
    consent_id: str
    subject_id: str
    verifier_id: str
    purpose: str
    authorized_credential_ids: list[str]
    valid_until: float
    status: str = "ACTIVE"  # "ACTIVE" | "REVOKED" | "EXPIRED"
    granted_at: float = field(default_factory=time.time)

class SubjectControlledConsentManager:
    def __init__(self):
        self._consents: dict[str, CitizenConsentGrant] = {}

    def grant_consent(
        self,
        subject_id: str,
        verifier_id: str,
        purpose: str,
        credential_ids: list[str],
        duration_days: int = 7
    ) -> CitizenConsentGrant:
        cid = f"cst_{secrets.token_hex(8)}"
        grant = CitizenConsentGrant(
            consent_id=cid,
            subject_id=subject_id,
            verifier_id=verifier_id,
            purpose=purpose,
            authorized_credential_ids=credential_ids,
            valid_until=time.time() + (duration_days * 86400)
        )
        self._consents[cid] = grant
        return grant

    def revoke_consent(self, consent_id: str, subject_id: str) -> bool:
        grant = self._consents.get(consent_id)
        if not grant or grant.subject_id != subject_id:
            return False
        grant.status = "REVOKED"
        return True

    def validate_consent(self, subject_id: str, verifier_id: str, purpose: str, credential_id: str) -> bool:
        now = time.time()
        for g in self._consents.values():
            if (
                g.subject_id == subject_id
                and g.verifier_id == verifier_id
                and g.purpose == purpose
                and credential_id in g.authorized_credential_ids
            ):
                if g.status == "ACTIVE" and g.valid_until > now:
                    return True
        return False
