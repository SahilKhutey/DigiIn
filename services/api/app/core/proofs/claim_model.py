"""
DigiIn Cryptographic Proof Subsystem — Claim Model & Privacy Minimization
Defines typed VerifiedClaims and claim filtering to ensure verifiers receive only purpose-bound assertions.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VerifiedClaim:
    type: str
    value: Any
    status: str = "VERIFIED"
    verified_at: float = 0.0
    source_id: str = "digiin_authoritative_source"
    verification_id: str = ""
    assurance_level: str = "HIGH"

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "value": self.value,
            "status": self.status,
            "verified_at": self.verified_at or time.time(),
            "source_id": self.source_id,
            "verification_id": self.verification_id,
            "assurance_level": self.assurance_level,
        }

class ClaimMinimizer:
    @staticmethod
    def minimize_claims(all_claims: list[VerifiedClaim], requested_types: list[str]) -> list[VerifiedClaim]:
        """
        Filter claims to only disclose what was strictly requested and authorized.
        Prevents full citizen PII or unrelated identity data from being included in the proof.
        """
        req_set = set(requested_types)
        return [c for c in all_claims if c.type in req_set]
