"""Anti-Piracy, Watermarking, and Anti-Replay Nonce Security Engine."""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid
from datetime import UTC, datetime
from typing import Any

WATERMARK_SECRET = b"digiin-anti-piracy-watermark-key-2026"


def generate_digital_watermark(
    document_id: str,
    owner_subject_id: str,
    audience: str = "PUBLIC_VERIFIER",
    purpose: str = "OFFICIAL_VERIFICATION",
) -> dict[str, Any]:
    """Generates a cryptographic anti-piracy watermark to prevent document counterfeiting."""
    now_iso = datetime.now(UTC).isoformat()
    watermark_id = f"wm_{uuid.uuid4().hex[:16]}"

    payload = f"{watermark_id}:{document_id}:{owner_subject_id}:{audience}:{purpose}:{now_iso}"
    seal_sig = hmac.new(WATERMARK_SECRET, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    return {
        "watermarkId": watermark_id,
        "documentId": document_id,
        "ownerSubjectId": owner_subject_id,
        "audience": audience,
        "purpose": purpose,
        "timestamp": now_iso,
        "antiPiracySeal": seal_sig,
        "antiCounterfeitNotice": "OFFICIAL SOVEREIGN DIGITAL CREDENTIAL — REPRODUCTION OR UNCONSENTED HARVESTING IS PROHIBITED",
    }


def verify_digital_watermark(watermark: dict[str, Any]) -> bool:
    """Verifies that an anti-piracy watermark seal has not been tampered with."""
    try:
        watermark_id = watermark["watermarkId"]
        doc_id = watermark["documentId"]
        owner_id = watermark["ownerSubjectId"]
        aud = watermark["audience"]
        purp = watermark["purpose"]
        ts = watermark["timestamp"]
        seal_sig = watermark["antiPiracySeal"]

        payload = f"{watermark_id}:{doc_id}:{owner_id}:{aud}:{purp}:{ts}"
        expected_sig = hmac.new(WATERMARK_SECRET, payload.encode("utf-8"), hashlib.sha256).hexdigest()

        return hmac.compare_digest(seal_sig, expected_sig)
    except (KeyError, TypeError):
        return False


class AntiReplayNonceManager:
    """Single-use nonce tracker preventing credential token replay and harvesting piracy."""

    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = ttl_seconds
        self._used_nonces: dict[str, float] = {}

    def generate_nonce(self) -> str:
        """Generates a cryptographically secure random single-use nonce."""
        nonce = f"nonce_{uuid.uuid4().hex}"
        return nonce

    def consume_nonce(self, nonce: str) -> bool:
        """Consumes a nonce atomically. Returns True if valid and unused; False if replayed."""
        now = time.time()
        self._purge_expired(now)

        if nonce in self._used_nonces:
            return False  # Replay attack detected

        self._used_nonces[nonce] = now + self.ttl_seconds
        return True

    def _purge_expired(self, now: float) -> None:
        expired = [n for n, exp in self._used_nonces.items() if exp < now]
        for n in expired:
            del self._used_nonces[n]


class CounterfeitFingerprintRegistry:
    """Detects pirated, revoked, or known forged credential SHA-256 fingerprints."""

    def __init__(self) -> None:
        self._blacklisted_hashes: set[str] = {
            # Known fraudulent sample templates
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "deadbeef00000000000000000000000000000000000000000000000000000000",
        }

    def is_flagged_counterfeit(self, file_sha256: str) -> bool:
        return file_sha256.lower() in self._blacklisted_hashes

    def flag_counterfeit(self, file_sha256: str, reason: str = "SUSPECTED_FORGERY") -> None:
        self._blacklisted_hashes.add(file_sha256.lower())


nonce_manager = AntiReplayNonceManager()
counterfeit_registry = CounterfeitFingerprintRegistry()
