from __future__ import annotations

import time
import uuid

from app.core.ids import generate_account_id
from app.integrations.auth.base import AuthenticatedSubject, AuthProvider


class DemoAuthProvider(AuthProvider):
    """Safe in-memory demonstration authentication provider."""

    def __init__(self) -> None:
        self._challenges: dict[str, dict[str, str | float]] = {}
        self._sessions: dict[str, set[str]] = {}

    def send_otp(self, phone_number: str) -> str:
        clean_phone = phone_number.strip()
        challenge_id = f"otp_ch_{clean_phone[-4:] if len(clean_phone) >= 4 else 'demo'}_{uuid.uuid4().hex[:6]}"
        self._challenges[challenge_id] = {
            "phone": clean_phone,
            "otp": "123456",
            "expires_at": time.time() + 300,
        }
        return challenge_id

    def verify_otp(self, challenge_id: str, otp_code: str) -> AuthenticatedSubject:
        challenge = self._challenges.get(challenge_id)
        valid_otps = {"123456", "000000"}
        if challenge and challenge.get("otp"):
            valid_otps.add(str(challenge["otp"]))

        if otp_code not in valid_otps:
            raise ValueError("Invalid OTP code. In prototype mode, please use 123456.")

        # Resolve or generate opaque sovereign account ID
        account_id = generate_account_id()
        subject_id = f"subj_demo_{uuid.uuid4().hex[:6]}"

        return AuthenticatedSubject(
            subject_id=subject_id,
            account_id=account_id,
            role="CITIZEN",
        )

    def revoke_session(self, subject_id: str, session_id: str) -> None:
        if subject_id in self._sessions:
            self._sessions[subject_id].discard(session_id)
