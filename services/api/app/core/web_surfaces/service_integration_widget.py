"""
DigiIn Web Surfaces — Service Integration Widget & Auth Flow
Provides the embeddable verification widget ("Continue with DigiIn"), authorization code generation, and minimal claim return.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuthorizationSession:
    code: str
    service_id: str
    purpose: str
    requested_claims: list[str]
    subject_account_id: str | None = None
    status: str = "PENDING_CONSENT"  # "PENDING_CONSENT" | "AUTHORIZED" | "EXCHANGED"
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 600)  # 10 minutes

class ServiceIntegrationWidgetService:
    def __init__(self):
        self._sessions: dict[str, AuthorizationSession] = {}

    def initiate_widget_flow(
        self,
        service_id: str,
        purpose: str,
        requested_claims: list[str]
    ) -> tuple[AuthorizationSession, str]:
        auth_code = f"dgi_code_{secrets.token_hex(16)}"
        session = AuthorizationSession(
            code=auth_code,
            service_id=service_id,
            purpose=purpose,
            requested_claims=requested_claims
        )
        self._sessions[auth_code] = session
        redirect_url = f"/requests/auth?code={auth_code}&service={service_id}&purpose={purpose}"
        return session, redirect_url

    def complete_citizen_consent(self, auth_code: str, subject_account_id: str) -> bool:
        session = self._sessions.get(auth_code)
        if not session or session.status != "PENDING_CONSENT" or session.expires_at < time.time():
            return False
        session.subject_account_id = subject_account_id
        session.status = "AUTHORIZED"
        return True

    def exchange_code_for_claims(self, auth_code: str, service_id: str) -> dict[str, Any] | None:
        session = self._sessions.get(auth_code)
        if not session or session.status != "AUTHORIZED" or session.service_id != service_id:
            return None
        session.status = "EXCHANGED"

        # Return minimal verified claims
        verified_claims = {c: "VERIFIED" for c in session.requested_claims}
        return {
            "status": "VERIFIED",
            "subjectReference": session.subject_account_id,
            "purpose": session.purpose,
            "claims": verified_claims,
            "verifiedAt": time.time()
        }
