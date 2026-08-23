from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class VerificationStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CredentialStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass(frozen=True)
class VerifiedClaim:
    claim_type: str
    value: str
    source: str
    verification_level: str
    verified_at: datetime


@dataclass(frozen=True)
class VerificationDecision:
    case_id: str
    account_id: str
    status: VerificationStatus
    decided_by: str
    decided_at: datetime


@dataclass(frozen=True)
class Credential:
    credential_id: str
    account_id: str
    credential_type: str
    issuer: str
    claims: tuple[VerifiedClaim, ...]
    issued_at: datetime
    expires_at: datetime | None
    status: CredentialStatus
    verification_case_id: str
