"""
DigiIn Long-Term Infrastructure — National Trust Registry
Provides authoritative, real-time trust lookup for Issuers and Verifiers without point-to-point hardcoding.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class TrustRegistryEntry:
    id: str
    organization_id: str
    organization_name: str
    role: str  # "ISSUER" | "VERIFIER" | "BOTH"
    accreditation_status: str  # "ACCREDITED" | "PROVISIONAL" | "SUSPENDED"
    assurance_level: str       # "A1_BASIC" to "A4_REGULATED"
    authorized_claim_types: list[str]
    public_keys: list[str]
    valid_from: float = field(default_factory=time.time)
    valid_until: float | None = None

class NationalTrustRegistry:
    def __init__(self):
        self._entries: dict[str, TrustRegistryEntry] = {}
        self._seed_default_participants()

    def _seed_default_participants(self):
        e1 = TrustRegistryEntry(
            id="iss_delhi_university",
            organization_id="org_delhi_univ",
            organization_name="University of Delhi",
            role="ISSUER",
            accreditation_status="ACCREDITED",
            assurance_level="A3_HIGH_ASSURANCE",
            authorized_claim_types=["education.degree", "education.transcript"],
            public_keys=["ed25519:pubkey:du_live_2026"]
        )
        e2 = TrustRegistryEntry(
            id="ver_scholarship_portal",
            organization_id="org_ministry_edu",
            organization_name="National Scholarship Portal",
            role="VERIFIER",
            accreditation_status="ACCREDITED",
            assurance_level="A3_HIGH_ASSURANCE",
            authorized_claim_types=["education.degree", "identity.name"],
            public_keys=["ed25519:pubkey:nsp_live_2026"]
        )
        self._entries[e1.id] = e1
        self._entries[e2.id] = e2

    def lookup_participant(self, participant_id: str) -> TrustRegistryEntry | None:
        return self._entries.get(participant_id)

    def is_trusted_issuer_for_claim(self, issuer_id: str, claim_type: str) -> bool:
        entry = self.lookup_participant(issuer_id)
        if not entry or entry.accreditation_status != "ACCREDITED":
            return False
        return claim_type in entry.authorized_claim_types or "*" in entry.authorized_claim_types
