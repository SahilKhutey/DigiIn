"""Verification Engine evaluating verification requests against registered issuers and predicate policies."""

from __future__ import annotations

from typing import Any
from services.verification.rules import (
    PredicateRule,
    evaluate_predicate_condition,
    score_evidence_match,
)


class VerificationEngine:
    """Core verification evaluation engine."""

    def evaluate_match(
        self,
        citizen_claims: dict[str, Any],
        registry_claims: dict[str, Any],
    ) -> dict[str, Any]:
        """Evaluate demographic match against authoritative state records."""
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

    def evaluate_predicates(
        self,
        rules: list[PredicateRule],
        attributes: dict[str, Any],
    ) -> dict[str, Any]:
        """Evaluate multiple zero-knowledge predicate conditions without disclosing raw claim data."""
        results = []
        all_passed = True

        for rule in rules:
            passed = evaluate_predicate_condition(rule, attributes)
            if not passed:
                all_passed = False
            results.append({
                "attribute": rule.attribute,
                "operator": rule.operator,
                "targetValue": rule.value,
                "satisfied": passed,
                "proofType": "DERIVED_ZERO_KNOWLEDGE_PREDICATE",
            })

        return {
            "allSatisfied": all_passed,
            "predicateResults": results,
            "disclosureLevel": "BOOLEAN_PREDICATE_ONLY",
        }


engine = VerificationEngine()
