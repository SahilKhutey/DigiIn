"""
DigiIn Institutional Scale — Onboarding Workflow Engine
Governs the 10-stage institutional onboarding state machine from Draft to Production.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any


class OnboardingState:
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    IDENTITY_VERIFIED = "IDENTITY_VERIFIED"
    TECHNICAL_REVIEW = "TECHNICAL_REVIEW"
    SECURITY_REVIEW = "SECURITY_REVIEW"
    APPROVED = "APPROVED"
    SANDBOX = "SANDBOX"
    CERTIFICATION = "CERTIFICATION"
    PRODUCTION = "PRODUCTION"
    REJECTED = "REJECTED"

VALID_TRANSITIONS = {
    OnboardingState.DRAFT: [OnboardingState.SUBMITTED],
    OnboardingState.SUBMITTED: [OnboardingState.UNDER_REVIEW, OnboardingState.REJECTED],
    OnboardingState.UNDER_REVIEW: [OnboardingState.IDENTITY_VERIFIED, OnboardingState.REJECTED],
    OnboardingState.IDENTITY_VERIFIED: [OnboardingState.TECHNICAL_REVIEW, OnboardingState.REJECTED],
    OnboardingState.TECHNICAL_REVIEW: [OnboardingState.SECURITY_REVIEW, OnboardingState.REJECTED],
    OnboardingState.SECURITY_REVIEW: [OnboardingState.APPROVED, OnboardingState.REJECTED],
    OnboardingState.APPROVED: [OnboardingState.SANDBOX],
    OnboardingState.SANDBOX: [OnboardingState.CERTIFICATION],
    OnboardingState.CERTIFICATION: [OnboardingState.PRODUCTION, OnboardingState.SANDBOX],
    OnboardingState.PRODUCTION: [],
    OnboardingState.REJECTED: [OnboardingState.DRAFT],
}

@dataclass
class OnboardingCase:
    id: str
    organization_id: str
    requested_capabilities: list[str]  # ["ISSUER", "VERIFIER"]
    requested_claim_types: list[str]
    status: str = OnboardingState.DRAFT
    assigned_reviewer: str | None = None
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    history: list[dict[str, Any]] = field(default_factory=list)

class OnboardingWorkflowEngine:
    def __init__(self):
        self._cases: dict[str, OnboardingCase] = {}

    def create_case(
        self,
        org_id: str,
        capabilities: list[str],
        claim_types: list[str]
    ) -> OnboardingCase:
        cid = f"onb_{secrets.token_hex(8)}"
        case = OnboardingCase(
            id=cid,
            organization_id=org_id,
            requested_capabilities=capabilities,
            requested_claim_types=claim_types,
            status=OnboardingState.DRAFT,
            history=[{"state": OnboardingState.DRAFT, "timestamp": time.time(), "actor": "SYSTEM"}]
        )
        self._cases[cid] = case
        return case

    def transition_state(
        self,
        case_id: str,
        target_state: str,
        actor: str,
        notes: str = ""
    ) -> tuple[bool, str, OnboardingCase | None]:
        case = self._cases.get(case_id)
        if not case:
            return False, "CASE_NOT_FOUND", None

        allowed = VALID_TRANSITIONS.get(case.status, [])
        if target_state not in allowed:
            return False, f"INVALID_TRANSITION: Cannot move from '{case.status}' to '{target_state}'.", case

        case.status = target_state
        now = time.time()
        case.history.append({"state": target_state, "timestamp": now, "actor": actor, "notes": notes})

        if target_state == OnboardingState.PRODUCTION:
            case.completed_at = now

        return True, f"TRANSITIONED_TO_{target_state}", case

    def get_case(self, case_id: str) -> OnboardingCase | None:
        return self._cases.get(case_id)
