from datetime import UTC, datetime

import pytest

from app.domain.credential_models import (
    CredentialStatus,
    VerificationDecision,
    VerificationStatus,
    VerifiedClaim,
)
from app.services.credential_issuer import CredentialIssuanceError, CredentialIssuer
from app.services.credential_verifier import CredentialVerifier


def approved_decision():
    return VerificationDecision(
        case_id="CASE-1",
        account_id="DIN-ABCD-EFGH-JKLM",
        status=VerificationStatus.APPROVED,
        decided_by="officer-1",
        decided_at=datetime.now(UTC),
    )


def claim():
    return VerifiedClaim(
        claim_type="full_name",
        value="Citizen",
        source="government-record",
        verification_level="verified",
        verified_at=datetime.now(UTC),
    )


def test_approved_case_can_issue_credential():
    credential = CredentialIssuer().issue(
        decision=approved_decision(),
        credential_type="identity.basic",
        issuer="DigiIn Demo Issuer",
        claims=(claim(),),
    )
    assert credential.status is CredentialStatus.ACTIVE
    assert credential.credential_id.startswith("CRD-")


def test_rejected_case_cannot_issue():
    decision = VerificationDecision(
        case_id="CASE-2",
        account_id="DIN-ABCD-EFGH-JKLM",
        status=VerificationStatus.REJECTED,
        decided_by="officer-1",
        decided_at=datetime.now(UTC),
    )
    with pytest.raises(CredentialIssuanceError):
        CredentialIssuer().issue(
            decision=decision,
            credential_type="identity.basic",
            issuer="issuer",
            claims=(claim(),),
        )


def test_unverified_claim_cannot_be_issued():
    bad_claim = VerifiedClaim(
        claim_type="full_name",
        value="Citizen",
        source="upload",
        verification_level="unverified",
        verified_at=datetime.now(UTC),
    )
    with pytest.raises(CredentialIssuanceError):
        CredentialIssuer().issue(
            decision=approved_decision(),
            credential_type="identity.basic",
            issuer="issuer",
            claims=(bad_claim,),
        )


def test_revoked_credential_is_invalid():
    credential = CredentialIssuer().issue(
        decision=approved_decision(),
        credential_type="identity.basic",
        issuer="issuer",
        claims=(claim(),),
    )
    revoked = credential.__class__(
        **{**credential.__dict__, "status": CredentialStatus.REVOKED}
    )
    result = CredentialVerifier().verify(revoked)
    assert result == {"valid": False, "reason": "revoked"}
