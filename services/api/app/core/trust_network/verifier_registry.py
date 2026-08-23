"""
DigiIn Trust Network & Interoperability — Verifier Registry
Manages authorized verifier organizations, permissible operational purposes, and API scopes.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


class VerifierStatus:
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"

@dataclass
class Verifier:
    id: str
    organization_id: str
    name: str
    status: str = VerifierStatus.ACTIVE
    allowed_claim_types: list[str] = field(default_factory=list)
    allowed_purposes: list[str] = field(default_factory=list)
    scopes: list[str] = field(default_factory=list)
    registered_at: float = field(default_factory=time.time)

class VerifierRegistry:
    def __init__(self):
        self._verifiers: dict[str, Verifier] = {}
        self._seed_default_verifiers()

    def _seed_default_verifiers(self):
        v1 = Verifier(
            id="ver_scholarship_portal",
            organization_id="org_ministry_education",
            name="National Scholarship Portal",
            status=VerifierStatus.ACTIVE,
            allowed_claim_types=["education.degree", "education.marksheet"],
            allowed_purposes=["SCHOLARSHIP_ELIGIBILITY", "ADMISSION_VERIFICATION"],
            scopes=["claims:request", "claims:verify", "proofs:verify"]
        )
        self._verifiers[v1.id] = v1

    def register_verifier(
        self,
        verifier_id: str,
        org_id: str,
        name: str,
        allowed_claims: list[str],
        allowed_purposes: list[str],
        scopes: list[str]
    ) -> Verifier:
        v = Verifier(
            id=verifier_id,
            organization_id=org_id,
            name=name,
            allowed_claim_types=allowed_claims,
            allowed_purposes=allowed_purposes,
            scopes=scopes
        )
        self._verifiers[verifier_id] = v
        return v

    def get_verifier(self, verifier_id: str) -> Verifier | None:
        return self._verifiers.get(verifier_id)

    def validate_verifier_access(self, verifier_id: str, claim_type: str, purpose: str) -> tuple[bool, str | None]:
        v = self.get_verifier(verifier_id)
        if not v or v.status != VerifierStatus.ACTIVE:
            return False, "VERIFIER_NOT_ACTIVE_OR_UNREGISTERED"

        if claim_type not in v.allowed_claim_types and "*" not in v.allowed_claim_types:
            return False, f"CLAIM_TYPE_NOT_PERMITTED: Claim '{claim_type}' is not authorized for verifier '{verifier_id}'."

        if purpose not in v.allowed_purposes and "*" not in v.allowed_purposes:
            return False, f"PURPOSE_NOT_PERMITTED: Purpose '{purpose}' is not authorized for verifier '{verifier_id}'."

        return True, None
