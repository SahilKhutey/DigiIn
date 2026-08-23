from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


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


# --- Pydantic API Schemas ---

class VerifiedClaimSchema(BaseModel):
    claim_type: str
    value: str
    source: str
    verification_level: str = "verified"
    verified_at: datetime | None = None


class IssueCredentialRequest(BaseModel):
    case_id: str
    account_id: str
    credential_type: str
    issuer: str = "DigiIn Sovereign Issuer"
    claims: list[VerifiedClaimSchema]
    expires_at: datetime | None = None


class CredentialResponse(BaseModel):
    credential_id: str
    account_id: str
    credential_type: str
    issuer: str
    claims: list[VerifiedClaimSchema]
    issued_at: datetime
    expires_at: datetime | None = None
    status: str
    verification_case_id: str


class VerifyCredentialRequest(BaseModel):
    credential_id: str


class VerifyCredentialResponse(BaseModel):
    valid: bool
    reason: str
    credential_id: str | None = None
    credential_type: str | None = None
    issuer: str | None = None
    issued_at: datetime | None = None
    expires_at: datetime | None = None


class RevokeCredentialRequest(BaseModel):
    reason: str = Field(default="Revoked by authority / citizen request")
