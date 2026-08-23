from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.gateway_models import Consent, RequestStatus, VerificationRequest
from app.services.disclosure_policy import authorize_disclosure


def _to_utc(dt: datetime | None) -> datetime:
    if dt is None:
        return datetime.now(UTC)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


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
    ) -> dict[str, Any]:
        now = datetime.now(UTC)

        if request.status is RequestStatus.REVOKED or consent.revoked_at is not None:
            return {"valid": False, "reason": "request_or_consent_revoked"}

        if request.status is not RequestStatus.APPROVED:
            return {"valid": False, "reason": "request_not_approved"}

        if _to_utc(request.expires_at) <= now:
            return {"valid": False, "reason": "request_expired"}

        if _to_utc(consent.expires_at) <= now:
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
