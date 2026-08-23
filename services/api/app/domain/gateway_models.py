from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class RequestStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass(frozen=True)
class VerificationRequest:
    request_id: str
    verifier_id: str
    account_id: str
    purpose: str
    requested_claim_types: tuple[str, ...]
    status: RequestStatus
    expires_at: datetime
    created_at: datetime


@dataclass(frozen=True)
class Consent:
    consent_id: str
    request_id: str
    account_id: str
    decision: str
    approved_claim_types: tuple[str, ...]
    granted_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None


# --- Pydantic API Schemas ---

class CreateGatewayVerificationRequest(BaseModel):
    verifier_id: str
    account_id: str
    purpose: str
    requested_claim_types: list[str] = Field(min_length=1)
    ttl_minutes: int = Field(default=30, ge=1, le=1440)


class GatewayVerificationRequestResponse(BaseModel):
    request_id: str
    verifier_id: str
    account_id: str
    purpose: str
    requested_claim_types: list[str]
    status: str
    created_at: datetime
    expires_at: datetime


class GatewayConsentApproveRequest(BaseModel):
    approved_claim_types: list[str] = Field(min_length=1)
    ttl_minutes: int = Field(default=60, ge=1, le=1440)


class GatewayConsentResponse(BaseModel):
    consent_id: str
    request_id: str
    account_id: str
    decision: str
    approved_claim_types: list[str]
    granted_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None


class ProofSchema(BaseModel):
    proof_id: str
    issuer: str
    audience: str
    issued_at: int
    expires_at: int
    nonce: str
    claims: dict[str, Any]
    key_id: str
    signature: str


class GatewayEvaluateResponse(BaseModel):
    valid: bool
    reason: str | None = None
    request_id: str | None = None
    purpose: str | None = None
    claims: dict[str, str] = Field(default_factory=dict)
    generated_at: datetime | None = None
    proof: ProofSchema | None = None


class VerifyProofRequest(BaseModel):
    proof: ProofSchema
    expected_issuer: str = "digiin"
    expected_audience: str
    expected_nonce: str


class VerifyProofResponse(BaseModel):
    valid: bool
    status: str
    issuer: str | None = None
    audience: str | None = None
    claims: dict[str, Any] = Field(default_factory=dict)
    key_id: str | None = None
    reason: str | None = None
