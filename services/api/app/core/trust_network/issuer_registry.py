"""
DigiIn Trust Network & Interoperability — Issuer Registry
Manages authoritative claim issuers, accreditation status, trust levels (Level 0-4), and supported claim types.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


class IssuerTrustLevel:
    LEVEL_0_UNVERIFIED = 0
    LEVEL_1_ORG_VERIFIED = 1
    LEVEL_2_AUTHORITY_VERIFIED = 2
    LEVEL_3_APPROVED_ISSUER = 3
    LEVEL_4_HIGH_ASSURANCE = 4

class IssuerStatus:
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"

@dataclass
class Issuer:
    id: str
    organization_id: str
    name: str
    trust_level: int = IssuerTrustLevel.LEVEL_1_ORG_VERIFIED
    status: str = IssuerStatus.PENDING
    supported_claim_types: list[str] = field(default_factory=list)
    trust_profile_id: str = "tp_standard_authority"
    registered_at: float = field(default_factory=time.time)

class IssuerRegistry:
    def __init__(self):
        self._issuers: dict[str, Issuer] = {}
        self._seed_default_issuers()

    def _seed_default_issuers(self):
        i1 = Issuer(
            id="iss_cbse_central",
            organization_id="org_cbse_board",
            name="Central Board of Secondary Education",
            trust_level=IssuerTrustLevel.LEVEL_4_HIGH_ASSURANCE,
            status=IssuerStatus.ACTIVE,
            supported_claim_types=["education.marksheet", "education.secondary_certificate"],
            trust_profile_id="tp_statutory_education_authority"
        )
        i2 = Issuer(
            id="iss_delhi_university",
            organization_id="org_delhi_univ",
            name="University of Delhi",
            trust_level=IssuerTrustLevel.LEVEL_3_APPROVED_ISSUER,
            status=IssuerStatus.ACTIVE,
            supported_claim_types=["education.degree", "education.transcript"],
            trust_profile_id="tp_accredited_university"
        )
        self._issuers[i1.id] = i1
        self._issuers[i2.id] = i2

    def register_issuer(
        self,
        issuer_id: str,
        org_id: str,
        name: str,
        trust_level: int,
        supported_claim_types: list[str]
    ) -> Issuer:
        iss = Issuer(
            id=issuer_id,
            organization_id=org_id,
            name=name,
            trust_level=trust_level,
            status=IssuerStatus.ACTIVE,
            supported_claim_types=supported_claim_types
        )
        self._issuers[issuer_id] = iss
        return iss

    def get_issuer(self, issuer_id: str) -> Issuer | None:
        return self._issuers.get(issuer_id)

    def is_issuer_authorized_for_claim(self, issuer_id: str, claim_type: str) -> bool:
        iss = self.get_issuer(issuer_id)
        if not iss or iss.status != IssuerStatus.ACTIVE:
            return False
        return claim_type in iss.supported_claim_types
