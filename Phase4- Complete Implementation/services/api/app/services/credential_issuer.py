from __future__ import annotations

from datetime import datetime, timezone

from app.core.credential_ids import generate_credential_id
from app.domain.credential_models import (
    Credential,
    CredentialStatus,
    VerificationDecision,
    VerificationStatus,
    VerifiedClaim,
)


class CredentialIssuanceError(ValueError):
    pass


class CredentialIssuer:
    """Domain-level credential issuance policy.

    Persistence, signing and external issuer adapters belong outside this
    service. This layer enforces the issuance invariants.
    """

    def issue(
        self,
        *,
        decision: VerificationDecision,
        credential_type: str,
        issuer: str,
        claims: tuple[VerifiedClaim, ...],
        expires_at=None,
    ) -> Credential:
        if decision.status is not VerificationStatus.APPROVED:
            raise CredentialIssuanceError(
                "credentials can only be issued from an approved case"
            )

        if not claims:
            raise CredentialIssuanceError(
                "at least one verified claim is required"
            )

        if any(claim.verification_level == "unverified" for claim in claims):
            raise CredentialIssuanceError(
                "unverified claims cannot be included in a credential"
            )

        return Credential(
            credential_id=generate_credential_id(),
            account_id=decision.account_id,
            credential_type=credential_type,
            issuer=issuer,
            claims=claims,
            issued_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            status=CredentialStatus.ACTIVE,
            verification_case_id=decision.case_id,
        )
