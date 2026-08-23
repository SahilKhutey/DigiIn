from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


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
