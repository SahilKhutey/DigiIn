"""
DigiIn Trust Network Expansion — Issuer & Verifier Accreditation & Assurance Framework
Maintains formal accreditation lifecycles, 4-tier assurance profiles (A1-A4), and internal organizational trust states.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field


class AssuranceProfile:
    A1_BASIC = "A1_BASIC"
    A2_VERIFIED_ORG = "A2_VERIFIED_ORG"
    A3_HIGH_ASSURANCE = "A3_HIGH_ASSURANCE"
    A4_REGULATED = "A4_REGULATED"

class AccreditationStatus:
    APPLICATION = "APPLICATION"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACCREDITED = "ACCREDITED"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"

class OrgTrustState:
    TRUSTED = "TRUSTED"
    MONITORED = "MONITORED"
    RESTRICTED = "RESTRICTED"
    SUSPENDED = "SUSPENDED"

@dataclass
class OrganizationAccreditation:
    id: str
    organization_id: str
    accreditation_type: str  # "ISSUER" | "VERIFIER"
    status: str = AccreditationStatus.ACCREDITED
    assurance_profile: str = AssuranceProfile.A3_HIGH_ASSURANCE
    approved_claim_types: list[str] = field(default_factory=list)
    approved_purposes: list[str] = field(default_factory=list)
    trust_state: str = OrgTrustState.TRUSTED
    accredited_at: float = field(default_factory=time.time)
    expires_at: float | None = None

class AccreditationEngine:
    def __init__(self):
        self._accreditations: dict[str, OrganizationAccreditation] = {}
        self._seed_default_accreditations()

    def _seed_default_accreditations(self):
        acc1 = OrganizationAccreditation(
            id="acc_du_issuer",
            organization_id="org_delhi_univ",
            accreditation_type="ISSUER",
            status=AccreditationStatus.ACCREDITED,
            assurance_profile=AssuranceProfile.A4_REGULATED,
            approved_claim_types=["education.degree", "education.transcript"],
            trust_state=OrgTrustState.TRUSTED
        )
        acc2 = OrganizationAccreditation(
            id="acc_scholarship_verifier",
            organization_id="org_ministry_education",
            accreditation_type="VERIFIER",
            status=AccreditationStatus.ACCREDITED,
            assurance_profile=AssuranceProfile.A3_HIGH_ASSURANCE,
            approved_claim_types=["education.degree", "education.marksheet"],
            approved_purposes=["SCHOLARSHIP_ELIGIBILITY", "ADMISSION_VERIFICATION"],
            trust_state=OrgTrustState.TRUSTED
        )
        self._accreditations[acc1.organization_id + ":ISSUER"] = acc1
        self._accreditations[acc2.organization_id + ":VERIFIER"] = acc2

    def accredit_organization(
        self,
        org_id: str,
        accreditation_type: str,
        assurance_profile: str,
        approved_claims: list[str],
        approved_purposes: list[str]
    ) -> OrganizationAccreditation:
        aid = f"acc_{secrets.token_hex(8)}"
        acc = OrganizationAccreditation(
            id=aid,
            organization_id=org_id,
            accreditation_type=accreditation_type,
            status=AccreditationStatus.ACCREDITED,
            assurance_profile=assurance_profile,
            approved_claim_types=approved_claims,
            approved_purposes=approved_purposes,
            trust_state=OrgTrustState.TRUSTED
        )
        key = f"{org_id}:{accreditation_type}"
        self._accreditations[key] = acc
        return acc

    def get_accreditation(self, org_id: str, accreditation_type: str) -> OrganizationAccreditation | None:
        return self._accreditations.get(f"{org_id}:{accreditation_type}")

    def is_issuer_accredited_for_claim(self, org_id: str, claim_type: str) -> bool:
        acc = self.get_accreditation(org_id, "ISSUER")
        if not acc or acc.status != AccreditationStatus.ACCREDITED or acc.trust_state == OrgTrustState.SUSPENDED:
            return False
        return claim_type in acc.approved_claim_types or "*" in acc.approved_claim_types

    def is_verifier_accredited(self, org_id: str, claim_type: str, purpose: str) -> tuple[bool, str | None]:
        acc = self.get_accreditation(org_id, "VERIFIER")
        if not acc or acc.status != AccreditationStatus.ACCREDITED:
            return False, "VERIFIER_NOT_ACCREDITED"
        if acc.trust_state == OrgTrustState.SUSPENDED:
            return False, "VERIFIER_TRUST_STATE_SUSPENDED"
        if claim_type not in acc.approved_claim_types and "*" not in acc.approved_claim_types:
            return False, f"CLAIM_TYPE_NOT_ACCREDITED: Claim '{claim_type}' is outside approved verifier scope."
        if purpose not in acc.approved_purposes and "*" not in acc.approved_purposes:
            return False, f"PURPOSE_NOT_ACCREDITED: Purpose '{purpose}' is outside approved verifier scope."
        return True, None
