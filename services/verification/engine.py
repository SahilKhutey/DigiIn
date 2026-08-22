"""Verification Engine evaluating verification requests against registered issuers."""

from __future__ import annotations

from typing import Any
from services.verification.rules import score_evidence_match


class VerificationEngine:
    """Core verification evaluation engine."""

    def __init__(self) -> None:
        pass

    def evaluate_match(
        self,
        citizen_claims: dict[str, Any],
        registry_claims: dict[str, Any],
    ) -> dict[str, Any]:
        score = score_evidence_match(citizen_claims, registry_claims)
        if score >= 95.0:
            verdict = "VERIFIED"
            level = 4
        elif score >= 70.0:
            verdict = "REQUIRES_REVIEW"
            level = 2
        else:
            verdict = "IDENTITY_MISMATCH"
            level = 0

        return {
            "score": score,
            "verdict": verdict,
            "verificationLevel": level,
        }
