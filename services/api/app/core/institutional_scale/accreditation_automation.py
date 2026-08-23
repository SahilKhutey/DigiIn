"""
DigiIn Institutional Scale — Automated Accreditation Engine
Evaluates 9-point accreditation criteria before authorizing institutional issuer/verifier capabilities.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field

MANDATORY_ACCREDITATION_CRITERIA = [
    "org_identity",
    "authority_evidence",
    "domain_ownership",
    "security_contact",
    "integration_test",
    "webhook_test",
    "credential_test",
    "privacy_assessment",
    "claim_authority",
]

@dataclass
class AccreditationEvaluation:
    id: str
    organization_id: str
    passed: bool
    evaluated_criteria: dict[str, bool]
    reviewer_id: str
    decision_notes: str
    policy_version: str = "2026.08"
    evaluated_at: float = field(default_factory=time.time)

class AutomatedAccreditationChecker:
    def __init__(self):
        self._evaluations: dict[str, AccreditationEvaluation] = {}

    def evaluate_organization(
        self,
        org_id: str,
        criteria_checks: dict[str, bool],
        reviewer_id: str,
        notes: str = ""
    ) -> tuple[bool, AccreditationEvaluation]:
        missing = [c for c in MANDATORY_ACCREDITATION_CRITERIA if not criteria_checks.get(c, False)]
        passed = len(missing) == 0

        eid = f"evl_{secrets.token_hex(8)}"
        eval_record = AccreditationEvaluation(
            id=eid,
            organization_id=org_id,
            passed=passed,
            evaluated_criteria=criteria_checks,
            reviewer_id=reviewer_id,
            decision_notes=notes or ("All criteria verified" if passed else f"Missing: {', '.join(missing)}")
        )
        self._evaluations[org_id] = eval_record
        return passed, eval_record

    def get_evaluation(self, org_id: str) -> AccreditationEvaluation | None:
        return self._evaluations.get(org_id)
