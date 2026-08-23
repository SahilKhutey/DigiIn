from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AuthenticatedSubject:
    subject_id: str
    account_id: str
    role: str


class AuthProvider(Protocol):
    """Provider boundary between DigiIn domain logic and authentication."""

    def send_otp(self, phone_number: str) -> str:
        ...

    def verify_otp(self, challenge_id: str, otp_code: str) -> AuthenticatedSubject:
        ...

    def revoke_session(self, subject_id: str, session_id: str) -> None:
        ...
