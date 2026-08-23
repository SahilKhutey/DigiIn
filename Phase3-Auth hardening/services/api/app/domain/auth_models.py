from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AuthChallengeRecord:
    challenge_id: str
    account_id: str
    challenge_hash: str
    expires_at: datetime
    attempts: int = 0
    consumed_at: datetime | None = None


@dataclass(frozen=True)
class SessionRecord:
    session_id: str
    account_id: str
    token_family: str
    refresh_token_hash: str
    expires_at: datetime
    revoked_at: datetime | None = None
    last_used_at: datetime | None = None
