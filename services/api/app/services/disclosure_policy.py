from __future__ import annotations

from app.domain.gateway_models import Consent, VerificationRequest


class DisclosurePolicyError(ValueError):
    pass


def authorize_disclosure(
    request: VerificationRequest,
    consent: Consent,
    available_claims: dict[str, str],
) -> dict[str, str]:
    """Apply purpose-bound selective disclosure policy.

    Guarantees:
    1. Account matches request and consent.
    2. Consent belongs strictly to the specific request ID.
    3. Consent is not revoked.
    4. Approved claims are a strict subset of requested claims.
    5. Returns ONLY approved claims from verified available claims.
    """
    if request.account_id != consent.account_id:
        raise DisclosurePolicyError("consent/account mismatch")

    if request.request_id != consent.request_id:
        raise DisclosurePolicyError("consent/request mismatch")

    if consent.revoked_at is not None:
        raise DisclosurePolicyError("consent has been revoked")

    approved = set(consent.approved_claim_types)
    requested = set(request.requested_claim_types)

    if not approved.issubset(requested):
        raise DisclosurePolicyError("consent exceeds requested disclosure")

    return {
        claim_type: value
        for claim_type, value in available_claims.items()
        if claim_type in approved
    }
