"""
DigiIn Institutional Review — Review Queue & Decision Engine
Manages the institutional review queue (/institution/review), records departmental decisions (Approved / Rejected), and maintains chronological request timelines.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any

from .institutional_request_engine import DepartmentVerificationRequest
from .organization_hierarchy import InstitutionalRBACGuard, InstitutionalUser


class InstitutionalDecisionType:
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"
    ESCALATED = "ESCALATED"

@dataclass
class InstitutionalDecision:
    id: str
    request_id: str
    decision: str  # "APPROVED" | "REJECTED" | "ESCALATED"
    reason: str
    decided_by_user_id: str
    decided_by_name: str
    notes: str | None = None
    decided_at: float = field(default_factory=time.time)

class InstitutionalReviewManager:
    def __init__(self):
        self._decisions: dict[str, InstitutionalDecision] = {}

    def get_review_queue(
        self,
        requests: list[DepartmentVerificationRequest],
        status_filter: str | None = None,
        department_filter: str | None = None
    ) -> list[DepartmentVerificationRequest]:
        queue = requests
        if department_filter:
            queue = [r for r in queue if r.department_id == department_filter]
        if status_filter:
            queue = [r for r in queue if r.status == status_filter]
        return queue

    def record_verification_result(
        self,
        request: DepartmentVerificationRequest,
        verification_status: str,
        assurance_level: str,
        verified_claims: dict[str, Any]
    ):
        now = time.time()
        request.status = "IN_REVIEW" if verification_status == "VERIFIED" else "FAILED"
        request.verification_result = {
            "status": verification_status,
            "assuranceLevel": assurance_level,
            "claims": verified_claims,
            "verifiedAt": now
        }
        request.timeline.append({
            "event": "CRYPTOGRAPHIC_VERIFICATION_COMPLETED",
            "timestamp": now,
            "actor": "DIGIIN_ENGINE",
            "description": f"DigiIn verified credentials ({verification_status})"
        })

    def record_institutional_decision(
        self,
        user: InstitutionalUser,
        request: DepartmentVerificationRequest,
        decision: str,
        reason: str,
        notes: str | None = None
    ) -> tuple[bool, InstitutionalDecision | None, str]:
        # 1. Check authorization
        ok_auth, msg = InstitutionalRBACGuard.is_authorized(user, "decisions:create", request.department_id)
        if not ok_auth:
            return False, None, msg

        if not request.verification_result or request.verification_result.get("status") != "VERIFIED":
            return False, None, "CANNOT_DECIDE_UNVERIFIED_REQUEST: Credential verification must be complete first"

        did = f"dec_{secrets.token_hex(8)}"
        now = time.time()

        dec = InstitutionalDecision(
            id=did,
            request_id=request.request_id,
            decision=decision,
            reason=reason,
            decided_by_user_id=user.id,
            decided_by_name=user.name,
            notes=notes,
            decided_at=now
        )
        self._decisions[did] = dec

        # Update request state & timeline
        request.institutional_decision = {
            "decisionId": did,
            "decision": decision,
            "reason": reason,
            "decidedBy": user.name,
            "decidedAt": now
        }
        request.status = "COMPLETED" if decision == InstitutionalDecisionType.APPROVED else "REJECTED"
        request.timeline.append({
            "event": f"INSTITUTIONAL_DECISION_{decision}",
            "timestamp": now,
            "actor": user.name,
            "description": f"Department decision recorded: {decision} ({reason})"
        })

        return True, dec, "DECISION_RECORDED_SUCCESSFULLY"

    def get_decision(self, decision_id: str) -> InstitutionalDecision | None:
        return self._decisions.get(decision_id)
