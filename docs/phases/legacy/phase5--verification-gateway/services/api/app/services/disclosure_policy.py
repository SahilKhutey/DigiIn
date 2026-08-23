from __future__ import annotations

from app.domain.gateway_models import Consent, VerificationRequest


class DisclosurePolicyError(ValueError):
    pass


def authorize_disclosure(
    request: VerificationRequest,
    consent: Consent,
    available_claims: dict[str, str],
) -> dict[str, str]:
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
