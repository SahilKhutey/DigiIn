"""
DigiIn Trust Network & Interoperability — Standardized Trust Protocol Adapter
Exposes stable, protocol-neutral trust interfaces: issue_claim, present_claim, verify_claim, and check_status.
"""

from __future__ import annotations

import time
from typing import Any

from .claim_model import ClaimIssuanceEngine, VerifiedClaimRecord
from .claim_presentation import ClaimPresentation, ClaimPresentationEngine
from .claim_schema import ClaimSchemaRegistry
from .issuer_registry import IssuerRegistry
from .verifier_registry import VerifierRegistry


class TrustProtocolAdapter:
    def __init__(
        self,
        issuer_reg: IssuerRegistry,
        verifier_reg: VerifierRegistry,
        schema_reg: ClaimSchemaRegistry,
        issuance_engine: ClaimIssuanceEngine,
        presentation_engine: ClaimPresentationEngine
    ):
        self.issuer_reg = issuer_reg
        self.verifier_reg = verifier_reg
        self.schema_reg = schema_reg
        self.issuance_engine = issuance_engine
        self.presentation_engine = presentation_engine

    def issue_claim(
        self,
        issuer_id: str,
        subject_id: str,
        claim_type: str,
        payload: dict[str, Any]
    ) -> tuple[bool, str | None, VerifiedClaimRecord | None]:
        return self.issuance_engine.issue_claim(
            issuer_id=issuer_id,
            subject_id=subject_id,
            claim_type=claim_type,
            value=payload
        )

    def present_claim(
        self,
        subject_id: str,
        verifier_id: str,
        purpose: str,
        claim_ids: list[str],
        nonce: str | None = None
    ) -> tuple[bool, str | None, ClaimPresentation | None]:
        return self.presentation_engine.create_presentation(
            subject_id=subject_id,
            verifier_id=verifier_id,
            purpose=purpose,
            claim_ids=claim_ids,
            nonce=nonce
        )

    def verify_claim(
        self,
        presentation: ClaimPresentation,
        expected_verifier_id: str,
        expected_purpose: str,
        expected_nonce: str | None = None
    ) -> tuple[bool, str]:
        return self.presentation_engine.verify_presentation(
            presentation=presentation,
            expected_verifier_id=expected_verifier_id,
            expected_purpose=expected_purpose,
            expected_nonce=expected_nonce
        )

    def check_status(self, claim_id: str) -> dict[str, Any]:
        status = self.issuance_engine.check_claim_status(claim_id)
        claim = self.issuance_engine.get_claim(claim_id)
        return {
            "claimId": claim_id,
            "status": status,
            "exists": claim is not None,
            "checkedAt": time.time()
        }
