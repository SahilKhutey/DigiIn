"""
DigiIn Privacy & Data Governance — Citizen Data Export Service
Builds structured GDPR/DPDP compliant portable data export archives with signed short-lived download tokens.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from typing import Any


class DataExportService:
    def __init__(self, signing_secret: str = "export_signing_secret_2026"):
        self.signing_secret = signing_secret

    def generate_export_package(
        self,
        citizen_id: str,
        profile_data: dict[str, Any],
        verifications: list[dict[str, Any]],
        consents: list[dict[str, Any]],
        proofs: list[dict[str, Any]]
    ) -> dict[str, Any]:
        export_id = f"exp_{secrets.token_hex(8)}"
        now = time.time()
        expires_at = int(now + 86400)  # 24 hour download window

        package_manifest = {
            "exportId": export_id,
            "citizenId": citizen_id,
            "exportedAt": now,
            "expiresAt": expires_at,
            "sections": {
                "profile": profile_data,
                "verifications": verifications,
                "consents": consents,
                "proofs": proofs,
            },
            "compliance": "DPDP_ACT_2023_PORTABILITY_COMPLIANT"
        }

        # Generate HMAC download token
        token_payload = f"{export_id}:{citizen_id}:{expires_at}"
        download_token = hmac.new(
            self.signing_secret.encode("utf-8"),
            token_payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        return {
            "exportId": export_id,
            "downloadUrl": f"https://api.digiin.in/v1/privacy/export/{export_id}?token={download_token}",
            "expiresAt": expires_at,
            "package": package_manifest
        }
