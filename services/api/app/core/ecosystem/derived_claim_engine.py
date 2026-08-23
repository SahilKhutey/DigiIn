"""
DigiIn Trust Network Expansion — Multi-Issuer & Derived Claims Engine
Evaluates composite qualification rules across multiple independent claim issuers with transparent decision reasoning.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DerivedClaim:
    id: str
    subject_id: str
    derived_claim_type: str
    source_claims: list[str]
    rule_id: str
    result: str  # "ELIGIBLE" | "INELIGIBLE"
    status: str = "ACTIVE"
    evaluated_at: float = field(default_factory=time.time)
    audit_explanation: dict[str, Any] = field(default_factory=dict)

class CompositeClaimEngine:
    def __init__(self):
        self._rules = {
            "SCHOLARSHIP_ELIGIBILITY_V2": self._evaluate_scholarship_rule,
            "PROFESSIONAL_PRACTICE_ELIGIBILITY": self._evaluate_professional_rule,
        }

    def _evaluate_scholarship_rule(self, claims: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        # Requires education.degree = VERIFIED, percentage >= 60.0 or cgpa >= 7.0
        degree_status = claims.get("degree_status", "")
        cgpa = claims.get("cgpa", 0.0)

        eligible = (degree_status == "VERIFIED" and cgpa >= 7.0)
        explanation = {
            "rule": "SCHOLARSHIP_ELIGIBILITY_V2",
            "degreeVerified": degree_status == "VERIFIED",
            "cgpaSatisfied": cgpa >= 7.0,
            "cgpaActual": cgpa,
            "result": "ELIGIBLE" if eligible else "INELIGIBLE"
        }
        return "ELIGIBLE" if eligible else "INELIGIBLE", explanation

    def _evaluate_professional_rule(self, claims: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        degree_ok = claims.get("degree_status") == "VERIFIED"
        licence_ok = claims.get("licence_status") == "ACTIVE"
        eligible = degree_ok and licence_ok
        explanation = {
            "rule": "PROFESSIONAL_PRACTICE_ELIGIBILITY",
            "degreeVerified": degree_ok,
            "licenceActive": licence_ok,
            "result": "ELIGIBLE" if eligible else "INELIGIBLE"
        }
        return "ELIGIBLE" if eligible else "INELIGIBLE", explanation

    def evaluate_composite_claim(
        self,
        subject_id: str,
        derived_type: str,
        rule_id: str,
        source_claim_ids: list[str],
        claim_values: dict[str, Any]
    ) -> tuple[bool, DerivedClaim]:
        eval_fn = self._rules.get(rule_id)
        if not eval_fn:
            raise ValueError(f"RULE_NOT_FOUND: Rule '{rule_id}' is not registered.")

        outcome, explanation = eval_fn(claim_values)
        did = f"dclm_{secrets.token_hex(8)}"
        dclaim = DerivedClaim(
            id=did,
            subject_id=subject_id,
            derived_claim_type=derived_type,
            source_claims=source_claim_ids,
            rule_id=rule_id,
            result=outcome,
            audit_explanation=explanation
        )
        return outcome == "ELIGIBLE", dclaim
