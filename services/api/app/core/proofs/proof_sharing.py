"""
DigiIn Cryptographic Proof Subsystem — Privacy-Preserving Proof Sharing & QR Resolver
Generates temporary scoped proof share tokens and dynamic QR verification targets without leaking citizen PII into QR codes.
"""

from __future__ import annotations

import secrets
import time
from typing import Any


class ProofShareService:
    def __init__(self):
        self._shares: dict[str, dict[str, Any]] = {}

    def create_proof_share(
        self,
        proof_id: str,
        citizen_id: str,
        disclosed_claims: list[str],
        purpose: str | None = None,
        ttl_seconds: int = 3600  # 1 hour
    ) -> dict[str, Any]:
        """Create a temporary, purpose-scoped proof share token."""
        share_id = f"shr_{secrets.token_hex(12)}"
        now = time.time()
        share = {
            "id": share_id,
            "proof_id": proof_id,
            "citizen_id": citizen_id,
            "disclosed_claims": disclosed_claims,
            "purpose": purpose or "GENERAL_VERIFICATION",
            "created_at": now,
            "expires_at": now + ttl_seconds,
            "revoked_at": None,
            "qr_verification_url": f"https://verify.digiin.in/share/{share_id}",
        }
        self._shares[share_id] = share
        return share

    def resolve_proof_share(self, share_id: str, now: float | None = None) -> dict[str, Any] | None:
        current = now or time.time()
        share = self._shares.get(share_id)
        if not share:
            return None
        if share.get("revoked_at") is not None or current > share.get("expires_at", 0):
            return None
        return share

    def revoke_proof_share(self, share_id: str, citizen_id: str) -> bool:
        share = self._shares.get(share_id)
        if not share or share.get("citizen_id") != citizen_id:
            return False
        share["revoked_at"] = time.time()
        return True
