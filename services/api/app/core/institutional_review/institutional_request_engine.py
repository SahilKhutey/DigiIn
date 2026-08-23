"""
DigiIn Institutional Review — Department Request Creation Engine
Handles department-scoped verification request creation wizard.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any

from .organization_hierarchy import InstitutionalRBACGuard, InstitutionalUser


@dataclass
class DepartmentVerificationRequest:
    request_id: str
    organization_id: str
    department_id: str
    department_name: str
    created_by_user_id: str
    subject_reference: str  # "DGI-XXXX-XXXX-XXXX"
    purpose: str
    requested_claims: list[str]
    disclosure_mode: str
    status: str = "PENDING_CITIZEN"  # "PENDING_CITIZEN" | "CITIZEN_APPROVED" | "VERIFIED" | "IN_REVIEW" | "COMPLETED" | "REJECTED"
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + (7 * 86400))
    verification_result: dict[str, Any] | None = None
    institutional_decision: dict[str, Any] | None = None
    timeline: list[dict[str, Any]] = field(default_factory=list)

class DepartmentRequestEngine:
    def __init__(self):
        self._requests: dict[str, DepartmentVerificationRequest] = {}

    def create_request(
        self,
        user: InstitutionalUser,
        department_name: str,
        subject_reference: str,
        purpose: str,
        requested_claims: list[str],
        disclosure_mode: str = "MINIMAL",
        target_department_id: str | None = None
    ) -> tuple[bool, DepartmentVerificationRequest | None, str]:
        dept_id = target_department_id or user.department_id
        if not dept_id:
            return False, None, "MISSING_DEPARTMENT_ID"

        # Check authorization
        ok_auth, msg = InstitutionalRBACGuard.is_authorized(user, "requests:create", dept_id)
        if not ok_auth:
            return False, None, msg

        rid = f"vr_{secrets.token_hex(8)}"
        now = time.time()
        req = DepartmentVerificationRequest(
            request_id=rid,
            organization_id=user.organization_id,
            department_id=dept_id,
            department_name=department_name,
            created_by_user_id=user.id,
            subject_reference=subject_reference,
            purpose=purpose,
            requested_claims=requested_claims,
            disclosure_mode=disclosure_mode,
            timeline=[
                {"event": "REQUEST_CREATED", "timestamp": now, "actor": user.name, "description": "Verification request created"}
            ]
        )
        self._requests[rid] = req
        return True, req, "REQUEST_CREATED_SUCCESSFULLY"

    def get_request(self, request_id: str) -> DepartmentVerificationRequest | None:
        return self._requests.get(request_id)

    def list_requests_for_department(self, department_id: str) -> list[DepartmentVerificationRequest]:
        return [r for r in self._requests.values() if r.department_id == department_id]
