from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


@dataclass(frozen=True)
class AuthChallengeRecord:
    challenge_id: str
    account_id: str
    challenge_hash: str
    expires_at: datetime
    attempts: int = 0
    consumed_at: datetime | None = None
    channel: str = "SMS"


@dataclass(frozen=True)
class SessionRecord:
    session_id: str
    account_id: str
    token_family: str
    refresh_token_hash: str
    expires_at: datetime
    created_at: datetime | None = None
    revoked_at: datetime | None = None
    last_used_at: datetime | None = None


@dataclass(frozen=True)
class DigiInAccountRecord:
    id: str
    account_id: str
    phone_number: str
    role: str = "CITIZEN"
    status: str = "ACTIVE"
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True)
class IdentityClaimRecord:
    id: str
    account_id: str
    claim_type: str
    value_reference: str
    verification_level: int
    source: str
    verified_at: datetime | None = None


@dataclass(frozen=True)
class SecurityEventRecord:
    id: str
    account_id: str
    event_type: str
    timestamp: datetime
    request_id: str | None = None
    metadata: dict[str, Any] | None = None


# --- Pydantic API Models ---

class AuthChallengeRequest(BaseModel):
    phone_number: str = Field(min_length=10, max_length=20)
    channel: Literal["SMS", "WHATSAPP"] = "SMS"


class AuthChallengeResponse(BaseModel):
    challenge_id: str
    account_id: str
    channel: str
    expires_in_seconds: int = 300
    demo_otp_hint: str | None = "123456"
    message: str


class AuthChallengeVerifyRequest(BaseModel):
    challenge_id: str
    otp_code: str = Field(min_length=6, max_length=6)


class AuthChallengeVerifyResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 900
    account_id: str
    role: str = "CITIZEN"
    session_id: str


class RefreshTokenPayload(BaseModel):
    refresh_token: str


class SessionInfoResponse(BaseModel):
    session_id: str
    account_id: str
    token_family: str
    is_active: bool
    created_at: datetime
    expires_at: datetime
    last_used_at: datetime | None = None
