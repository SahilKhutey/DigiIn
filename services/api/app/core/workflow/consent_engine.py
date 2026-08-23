"""
DigiIn Core Workflow Engine — Purpose-Bound Claim-Level Consent Engine
Enforces purpose binding, granular claim consent grants/declines, and consent verification before verification runs.
"""

import secrets
import time
from typing import Any


class ConsentEngine:
    def __init__(self):
        self._consents: dict[str, dict[str, Any]] = {}

    def create_consent_grant(
        self,
        citizen_id: str,
        organisation_id: str,
        request_id: str,
        purpose: str,
        requested_claims: list[str],
        granted_claims: list[str],
        ttl_seconds: int = 86400 * 30  # 30 days
    ) -> dict[str, Any]:
        """Create an informed, purpose-bound, claim-level consent grant."""
        consent_id = f"cst_{secrets.token_hex(12)}"
        now = time.time()

        # Ensure citizen can only grant claims that were requested
        valid_granted = [c for c in granted_claims if c in requested_claims]

        consent = {
            "id": consent_id,
            "citizen_id": citizen_id,
            "organisation_id": organisation_id,
            "request_id": request_id,
            "purpose": purpose,
            "requested_claims": requested_claims,
            "granted_claims": valid_granted,
            "declined_claims": [c for c in requested_claims if c not in valid_granted],
            "status": "GRANTED",
            "created_at": now,
            "expires_at": now + ttl_seconds,
            "revoked_at": None,
            "version": 1
        }
        self._consents[consent_id] = consent
        return consent

    def require_valid_consent(
        self,
        citizen_id: str,
        organisation_id: str,
        purpose: str,
        required_claims: list[str]
    ) -> tuple[bool, str | None, dict[str, Any] | None]:
        """
        Verify that active, unexpired, non-revoked consent exists for the exact purpose and required claims.
        """
        now = time.time()
        for consent in self._consents.values():
            if (
                consent.get("citizen_id") == citizen_id
                and consent.get("organisation_id") == organisation_id
                and consent.get("purpose") == purpose
                and consent.get("status") == "GRANTED"
            ):
                # Check expiration
                if now > consent.get("expires_at", 0):
                    consent["status"] = "EXPIRED"
                    continue

                # Check revocation
                if consent.get("revoked_at") is not None:
                    consent["status"] = "REVOKED"
                    continue

                # Check claim coverage
                granted_set = set(consent.get("granted_claims", []))
                missing_claims = [c for c in required_claims if c not in granted_set]
                if missing_claims:
                    return False, f"CONSENT_SCOPE_INSUFFICIENT: Citizen declined required claim(s): {missing_claims}", consent

                return True, None, consent

        return False, f"CONSENT_REQUIRED: No active consent grant found for organisation '{organisation_id}' and purpose '{purpose}'.", None

    def revoke_consent(self, consent_id: str, citizen_id: str) -> tuple[bool, str | None]:
        consent = self._consents.get(consent_id)
        if not consent:
            return False, "CONSENT_NOT_FOUND"
        if consent.get("citizen_id") != citizen_id:
            return False, "FORBIDDEN_IDOR: Cannot revoke consent belonging to another citizen."

        consent["status"] = "REVOKED"
        consent["revoked_at"] = time.time()
        consent["version"] = consent.get("version", 1) + 1
        return True, None
