"""
DigiIn Trust Network Expansion — Advanced Proof Exchange & Selective Disclosure Engine
Supports minimal field-level selective disclosure and multi-claim bundle presentations.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MultiClaimPresentation:
    presentation_id: str
    subject_id: str
    target_verifier: str
    purpose: str
    disclosed_claims: list[dict[str, Any]]
    nonce: str
    issued_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 900)  # 15 min validity

class SelectiveDisclosureEngine:
    @staticmethod
    def project_selective_fields(full_claim_value: dict[str, Any], requested_fields: list[str]) -> dict[str, Any]:
        """Discloses only requested attributes, preserving citizen privacy."""
        if not requested_fields or "*" in requested_fields:
            return full_claim_value
        return {k: v for k, v in full_claim_value.items() if k in requested_fields}

class MultiClaimPresentationManager:
    def __init__(self):
        self.disclosure_engine = SelectiveDisclosureEngine()

    def create_presentation_bundle(
        self,
        subject_id: str,
        target_verifier: str,
        purpose: str,
        claims_with_requested_fields: list[dict[str, Any]],  # [{"claim_id": ..., "type": ..., "value": ..., "fields": [...]}]
        nonce: str | None = None
    ) -> MultiClaimPresentation:
        disclosed = []
        for item in claims_with_requested_fields:
            projected_value = self.disclosure_engine.project_selective_fields(
                full_claim_value=item.get("value", {}),
                requested_fields=item.get("fields", [])
            )
            disclosed.append({
                "claimId": item.get("claim_id"),
                "claimType": item.get("type"),
                "disclosedAttributes": projected_value,
                "issuerId": item.get("issuer_id")
            })

        pid = f"mpr_{secrets.token_hex(8)}"
        return MultiClaimPresentation(
            presentation_id=pid,
            subject_id=subject_id,
            target_verifier=target_verifier,
            purpose=purpose,
            disclosed_claims=disclosed,
            nonce=nonce or f"nce_{secrets.token_hex(8)}"
        )
