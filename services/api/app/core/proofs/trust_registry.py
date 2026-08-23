"""
DigiIn Cryptographic Proof Subsystem — Trust Registry
Maintains authorized, trusted proof issuers and allowed proof types.
"""

from __future__ import annotations

from typing import Any


class TrustedIssuer:
    def __init__(
        self,
        id: str,
        name: str,
        issuer_identifier: str,
        trusted_proof_types: list[str],
        status: str = "ACTIVE"
    ):
        self.id = id
        self.name = name
        self.issuer_identifier = issuer_identifier
        self.trusted_proof_types = trusted_proof_types
        self.status = status  # "ACTIVE" | "SUSPENDED" | "REVOKED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "issuer_identifier": self.issuer_identifier,
            "trusted_proof_types": self.trusted_proof_types,
            "status": self.status,
        }

class TrustRegistry:
    def __init__(self):
        self._issuers: dict[str, TrustedIssuer] = {}
        self._seed_default_issuers()

    def _seed_default_issuers(self):
        # Default authoritative DigiIn platform issuer
        self.register_issuer(
            TrustedIssuer(
                id="iss_digiin_root",
                name="DigiIn Sovereign Verification Authority",
                issuer_identifier="did:digiin:authority:root",
                trusted_proof_types=["EDUCATION_VERIFIED", "AGE_VERIFIED", "IDENTITY_VERIFIED", "EMPLOYMENT_VERIFIED"],
                status="ACTIVE"
            )
        )
        self.register_issuer(
            TrustedIssuer(
                id="iss_cbse_board",
                name="Central Board of Secondary Education (CBSE)",
                issuer_identifier="did:digiin:issuer:cbse",
                trusted_proof_types=["EDUCATION_VERIFIED"],
                status="ACTIVE"
            )
        )

    def register_issuer(self, issuer: TrustedIssuer):
        self._issuers[issuer.issuer_identifier] = issuer

    def get_issuer(self, issuer_identifier: str) -> TrustedIssuer | None:
        return self._issuers.get(issuer_identifier)

    def is_issuer_trusted(self, issuer_identifier: str, proof_type: str) -> bool:
        issuer = self._issuers.get(issuer_identifier)
        if not issuer or issuer.status != "ACTIVE":
            return False
        return proof_type in issuer.trusted_proof_types
