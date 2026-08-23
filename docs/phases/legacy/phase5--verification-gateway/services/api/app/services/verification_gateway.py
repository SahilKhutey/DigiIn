from __future__ import annotations

from datetime import datetime, timezone

from app.domain.gateway_models import Consent, RequestStatus, VerificationRequest
from app.services.disclosure_policy import authorize_disclosure


class VerificationGateway:
    """Purpose-bound minimum-disclosure gateway.

    Credential lookup and cryptographic proof generation remain injectable
    boundaries; this service applies request/consent disclosure policy.
    """

    def evaluate(
        self,
        request: VerificationRequest,
        consent: Consent,
        verified_claims: dict[str, str],
    ) -> dict:
        now = datetime.now(timezone.utc)

        if request.status is not RequestStatus.APPROVED:
            return {"valid": False, "reason": "request_not_approved"}

        if request.expires_at <= now:
            return {"valid": False, "reason": "request_expired"}

        if consent.expires_at <= now:
            return {"valid": False, "reason": "consent_expired"}

        disclosed = authorize_disclosure(
            request,
            consent,
            verified_claims,
        )

        return {
            "valid": True,
            "request_id": request.request_id,
            "purpose": request.purpose,
            "claims": disclosed,
            "generated_at": now,
        }
