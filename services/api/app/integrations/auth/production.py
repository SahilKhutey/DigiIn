from __future__ import annotations

from app.integrations.auth.base import AuthenticatedSubject, AuthProvider


class ProductionAuthProvider(AuthProvider):
    """Production provider boundary integration.

    In production mode, authenticates via sovereign identity gateway / KMS signing.
    Fails closed if production security credentials or gateways are not properly configured.
    """

    def __init__(self, auth_secret: str | None = None) -> None:
        if not auth_secret:
            raise RuntimeError("ProductionAuthProvider requires an authentic DIGIIN_AUTH_SECRET")
        self._auth_secret = auth_secret

    def send_otp(self, phone_number: str) -> str:
        raise NotImplementedError("Production SMS/Aadhaar OTP gateway not configured")

    def verify_otp(self, challenge_id: str, otp_code: str) -> AuthenticatedSubject:
        raise NotImplementedError("Production SMS/Aadhaar OTP gateway not configured")

    def revoke_session(self, subject_id: str, session_id: str) -> None:
        raise NotImplementedError("Production session revocation gateway not configured")
