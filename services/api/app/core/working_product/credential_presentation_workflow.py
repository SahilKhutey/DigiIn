"""
DigiIn Working Product — Credential Issuance & Presentation Workflow (Flow 3)
Executes: Issuer issuance -> Citizen wallet -> Presentation -> Verifier verification -> Revocation propagation.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any

from .auth_context import AuthContext
from .request_pipeline import DigiInRequest, DigiInResponse


@dataclass
class ProductCredential:
    id: str
    issuer_id: str
    subject_id: str
    credential_type: str
    claims: dict[str, Any]
    status: str = "ACTIVE"  # "ACTIVE" | "REVOKED"
    issued_at: float = field(default_factory=time.time)

class CredentialPresentationWorkflow:
    def __init__(self, activity_mgr: Any, notification_mgr: Any):
        self._credentials: dict[str, ProductCredential] = {}
        self.activity_mgr = activity_mgr
        self.notification_mgr = notification_mgr

    def issue_credential(
        self,
        issuer_id: str,
        subject_id: str,
        credential_type: str,
        claims: dict[str, Any]
    ) -> ProductCredential:
        cid = f"cred_{secrets.token_hex(8)}"
        cred = ProductCredential(
            id=cid,
            issuer_id=issuer_id,
            subject_id=subject_id,
            credential_type=credential_type,
            claims=claims,
            status="ACTIVE"
        )
        self._credentials[cid] = cred

        self.activity_mgr.record_activity(
            user_id=subject_id,
            action="CREDENTIAL_ISSUED",
            title=f"New credential issued: {credential_type}",
            details={"credentialId": cid, "issuerId": issuer_id}
        )
        return cred

    def handle_present_credential(
        self,
        request: DigiInRequest[dict[str, Any]],
        auth: AuthContext
    ) -> DigiInResponse[dict[str, Any]]:
        cred_id = request.payload.get("credentialId")
        cred = self._credentials.get(cred_id)
        if not cred:
            return DigiInResponse.fail(request.request_id, "CREDENTIAL_NOT_FOUND", "Credential does not exist")

        if cred.status != "ACTIVE":
            return DigiInResponse.fail(request.request_id, "CREDENTIAL_INVALID", f"Credential is {cred.status}")

        self.activity_mgr.record_activity(
            user_id=auth.user_id,
            action="CREDENTIAL_PRESENTED",
            title=f"Presented {cred.credential_type}",
            details={"verifierId": request.payload.get("verifierId")}
        )

        return DigiInResponse.ok(request.request_id, {
            "presentationToken": f"pres_{secrets.token_hex(16)}",
            "status": "VALID",
            "claims": cred.claims
        })

    def revoke_credential(self, cred_id: str, reason: str = "ADMINISTRATIVE_UPDATE") -> bool:
        cred = self._credentials.get(cred_id)
        if not cred:
            return False
        cred.status = "REVOKED"
        self.activity_mgr.record_activity(
            user_id=cred.subject_id,
            action="CREDENTIAL_REVOKED",
            title=f"Credential revoked: {cred.credential_type}",
            details={"credentialId": cred_id, "reason": reason}
        )
        return True
