from datetime import UTC, datetime, timedelta

import pytest

from app.domain.gateway_models import Consent, RequestStatus, VerificationRequest
from app.services.disclosure_policy import DisclosurePolicyError
from app.services.verification_gateway import VerificationGateway


def make_request():
    now = datetime.now(UTC)
    return VerificationRequest(
        request_id="REQ-1",
        verifier_id="dept-1",
        account_id="DIN-ABCD-EFGH-JKLM",
        purpose="Scholarship eligibility",
        requested_claim_types=("full_name", "income_band", "domicile"),
        status=RequestStatus.APPROVED,
        expires_at=now + timedelta(minutes=10),
        created_at=now,
    )


def make_consent(claims=("income_band",)):
    now = datetime.now(UTC)
    return Consent(
        consent_id="CON-1",
        request_id="REQ-1",
        account_id="DIN-ABCD-EFGH-JKLM",
        decision="approved",
        approved_claim_types=claims,
        granted_at=now,
        expires_at=now + timedelta(minutes=5),
    )


def test_gateway_returns_only_consented_claims():
    result = VerificationGateway().evaluate(
        make_request(),
        make_consent(("income_band",)),
        {
            "full_name": "Citizen",
            "income_band": "eligible",
            "domicile": "CG",
        },
    )

    assert result["valid"] is True
    assert result["claims"] == {"income_band": "eligible"}


def test_revoked_consent_is_rejected():
    consent = make_consent()
    consent = Consent(**{**consent.__dict__, "revoked_at": datetime.now(UTC)})

    with pytest.raises(DisclosurePolicyError):
        from app.services.disclosure_policy import authorize_disclosure
        authorize_disclosure(
            make_request(),
            consent,
            {"income_band": "eligible"},
        )


def test_expired_request_is_rejected():
    request = make_request()
    request = VerificationRequest(
        **{
            **request.__dict__,
            "expires_at": datetime.now(UTC) - timedelta(seconds=1),
        }
    )

    result = VerificationGateway().evaluate(
        request,
        make_consent(),
        {"income_band": "eligible"},
    )
    assert result == {"valid": False, "reason": "request_expired"}
