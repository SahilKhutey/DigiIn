"""
DigiIn Working Product — Institutional Verification & Citizen Consent Workflow (Flow 2)
Executes: Institution verification request -> Citizen review -> Purpose-bound consent approval/denial -> Presentation proof -> Verifier check.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any

from .auth_context import AuthContext
from .request_pipeline import DigiInRequest, DigiInResponse


@dataclass
class VerificationConsentRequest:
    request_id: str
    subject_id: str
    verifier_id: str
    verifier_name: str
    purpose: str
    requested_claims: list[str]
    status: str = "PENDING"  # "PENDING" | "APPROVED" | "DENIED"
    created_at: float = field(default_factory=time.time)

class InstitutionalConsentWorkflow:
    def __init__(self, activity_mgr: Any, notification_mgr: Any):
        self._requests: dict[str, VerificationConsentRequest] = {}
        self.activity_mgr = activity_mgr
        self.notification_mgr = notification_mgr

    def create_verification_request(
        self,
        verifier_id: str,
        verifier_name: str,
        subject_id: str,
        purpose: str,
        requested_claims: list[str]
    ) -> VerificationConsentRequest:
        rid = f"vreq_{secrets.token_hex(8)}"
        vreq = VerificationConsentRequest(
            request_id=rid,
            subject_id=subject_id,
            verifier_id=verifier_id,
            verifier_name=verifier_name,
            purpose=purpose,
            requested_claims=requested_claims,
            status="PENDING"
        )
        self._requests[rid] = vreq

        self.notification_mgr.send_notification(
            user_id=subject_id,
            type="CONSENT_REQUESTED",
            message=f"{verifier_name} is requesting access to your {', '.join(requested_claims)}."
        )
        return vreq

    def handle_approve_consent(
        self,
        request: DigiInRequest[dict[str, Any]],
        auth: AuthContext
    ) -> DigiInResponse[dict[str, Any]]:
        vreq_id = request.payload.get("verificationRequestId")
        vreq = self._requests.get(vreq_id)
        if not vreq:
            return DigiInResponse.fail(request.request_id, "REQUEST_NOT_FOUND", f"Verification request '{vreq_id}' not found")

        vreq.status = "APPROVED"

        self.activity_mgr.record_activity(
            user_id=auth.user_id,
            action="CONSENT_APPROVED",
            title=f"Consent granted to {vreq.verifier_name}",
            details={"purpose": vreq.purpose, "claims": vreq.requested_claims}
        )

        return DigiInResponse.ok(request.request_id, {
            "verificationRequestId": vreq_id,
            "status": "APPROVED",
            "proofToken": f"prf_token_{secrets.token_hex(16)}"
        })

    def handle_deny_consent(
        self,
        request: DigiInRequest[dict[str, Any]],
        auth: AuthContext
    ) -> DigiInResponse[dict[str, Any]]:
        vreq_id = request.payload.get("verificationRequestId")
        vreq = self._requests.get(vreq_id)
        if not vreq:
            return DigiInResponse.fail(request.request_id, "REQUEST_NOT_FOUND", f"Verification request '{vreq_id}' not found")

        vreq.status = "DENIED"

        self.activity_mgr.record_activity(
            user_id=auth.user_id,
            action="CONSENT_DENIED",
            title=f"Consent denied to {vreq.verifier_name}",
            details={"purpose": vreq.purpose}
        )

        return DigiInResponse.ok(request.request_id, {
            "verificationRequestId": vreq_id,
            "status": "DENIED"
        })
