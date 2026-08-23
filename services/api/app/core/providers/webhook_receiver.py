"""
DigiIn Provider Integration Subsystem — Webhook Ingestion & Replay Defense
Verifies HMAC-SHA256 provider webhook signatures, validates timestamp windows, and deduplicates event deliveries.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any


class WebhookReceiverService:
    def __init__(self, timestamp_tolerance_seconds: int = 300):
        self.timestamp_tolerance_seconds = timestamp_tolerance_seconds
        self._processed_event_ids: set[str] = set()

    def verify_and_ingest_webhook(
        self,
        provider_id: str,
        secret_key: str,
        payload_bytes: bytes,
        signature_header: str,
        timestamp_header: str,
        event_id: str,
        now: float | None = None
    ) -> tuple[bool, str | None, dict[str, Any] | None]:
        """
        Validate HMAC signature, enforce timestamp window (<5 min skew), and enforce event idempotency.
        """
        current_time = now or time.time()

        # 1. Timestamp Freshness Check
        try:
            ts = float(timestamp_header)
            if abs(current_time - ts) > self.timestamp_tolerance_seconds:
                return False, "WEBHOOK_EXPIRED: Timestamp outside 5-minute validity window (potential replay).", None
        except (ValueError, TypeError):
            return False, "INVALID_TIMESTAMP_HEADER", None

        # 2. Cryptographic Signature Verification (HMAC-SHA256)
        signed_payload = f"{timestamp_header}.".encode() + payload_bytes
        expected_sig = hmac.new(
            secret_key.encode("utf-8"),
            signed_payload,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_sig, signature_header):
            return False, "SIGNATURE_MISMATCH: Forged or invalid webhook signature header.", None

        # 3. Deduplication Check
        dedup_key = f"{provider_id}:{event_id}"
        if dedup_key in self._processed_event_ids:
            return False, "DUPLICATE_EVENT: Event ID already ingested and processed.", None

        self._processed_event_ids.add(dedup_key)

        try:
            parsed = json.loads(payload_bytes.decode("utf-8"))
            return True, None, parsed
        except Exception:
            return False, "MALFORMED_JSON_PAYLOAD", None
