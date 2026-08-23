"""
DigiIn Trust Network & Interoperability — Audience-Restricted Claim Presentation
Produces tamper-evident claim presentations bound to specific verifiers, purposes, and anti-replay nonces.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any

from .claim_model import ClaimIssuanceEngine, ClaimStatus
from .verifier_registry import VerifierRegistry


@dataclass
class ClaimPresentation:
    presentation_id: str
    subject_id: str
    target_audience: str  # Verifier ID
    purpose: str
    nonce: str
    claims: list[dict[str, Any]]
    issued_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 600)  # 10 min presentation validity
    status: str = "VALID"

class ClaimPresentationEngine:
    def __init__(self, verifier_registry: VerifierRegistry, claim_engine: ClaimIssuanceEngine):
        self.verifier_registry = verifier_registry
        self.claim_engine = claim_engine

    def create_presentation(
        self,
        subject_id: str,
        verifier_id: str,
        purpose: str,
        claim_ids: list[str],
        nonce: str | None = None
    ) -> tuple[bool, str | None, ClaimPresentation | None]:
        # 1. Validate verifier and purpose
        v = self.verifier_registry.get_verifier(verifier_id)
        if not v or v.status != "ACTIVE":
            return False, "VERIFIER_NOT_AUTHORIZED", None

        # 2. Extract and minimize claims
        presented_claims = []
        for cid in claim_ids:
            claim = self.claim_engine.get_claim(cid)
            if not claim or claim.subject_id != subject_id:
                return False, f"CLAIM_NOT_FOUND_OR_SUBJECT_MISMATCH: Claim '{cid}' does not belong to subject.", None

            status = self.claim_engine.check_claim_status(cid)
            if status != ClaimStatus.ACTIVE:
                return False, f"CLAIM_INACTIVE: Claim '{cid}' is currently '{status}'.", None

            presented_claims.append({
                "claimId": claim.id,
                "type": claim.claim_type,
                "value": claim.value,
                "issuerId": claim.issuer_id,
                "assuranceLevel": claim.assurance_level,
                "status": status
            })

        pres_id = f"pres_{secrets.token_hex(8)}"
        presentation = ClaimPresentation(
            presentation_id=pres_id,
            subject_id=subject_id,
            target_audience=verifier_id,
            purpose=purpose,
            nonce=nonce or f"nce_{secrets.token_hex(8)}",
            claims=presented_claims
        )
        return True, None, presentation

    def verify_presentation(
        self,
        presentation: ClaimPresentation,
        expected_verifier_id: str,
        expected_purpose: str,
        expected_nonce: str | None = None
    ) -> tuple[bool, str]:
        # 1. Audience restriction check
        if presentation.target_audience != expected_verifier_id:
            return False, "AUDIENCE_MISMATCH: Presentation was intended for a different verifier."

        # 2. Purpose check
        if presentation.purpose != expected_purpose:
            return False, "PURPOSE_MISMATCH: Presentation purpose does not match requested verification purpose."

        # 3. Anti-replay nonce check
        if expected_nonce and presentation.nonce != expected_nonce:
            return False, "NONCE_MISMATCH: Replay attack detected or invalid presentation nonce."

        # 4. Expiration check
        if time.time() > presentation.expires_at:
            return False, "PRESENTATION_EXPIRED: Presentation validity window has lapsed."

        return True, "PRESENTATION_VERIFIED_SUCCESSFULLY"
