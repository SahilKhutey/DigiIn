"""Phase 9.2 — Idempotency & Request Deduplication Engine.

Prevents dangerous double-issuance of credentials, duplicate verification cases,
and repeated external provider mutations using cryptographic fingerprinting and TTL caching.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class IdempotencyRecord:
    key: str
    fingerprint: str
    status_code: int
    response_body: dict[str, Any]
    created_at: float
    expires_at: float


class IdempotencyEngine:
    """In-memory & pluggable distributed idempotency coordination engine."""

    def __init__(self, default_ttl_seconds: int = 86400) -> None:
        self.default_ttl_seconds = default_ttl_seconds
        self._records: dict[str, IdempotencyRecord] = {}

    def compute_fingerprint(self, path: str, method: str, body: Any) -> str:
        """Generates a deterministic SHA-256 fingerprint from request context."""
        serialized = json.dumps(
            {"path": path, "method": method.upper(), "body": body or {}},
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def get_cached_response(
        self, idempotency_key: str, fingerprint: str | None = None
    ) -> tuple[bool, int | None, dict[str, Any] | None]:
        """Checks if a matching idempotent response is available.

        Returns:
            (is_cached: bool, status_code: int | None, response_body: dict | None)
        """
        now = time.time()
        record = self._records.get(idempotency_key)

        if not record:
            return False, None, None

        if now > record.expires_at:
            del self._records[idempotency_key]
            return False, None, None

        if fingerprint and record.fingerprint != fingerprint:
            # Conflict: same idempotency key with different payload
            raise ValueError(
                "Idempotency-Key collision: payload does not match original request."
            )

        return True, record.status_code, record.response_body

    def store_response(
        self,
        idempotency_key: str,
        fingerprint: str,
        status_code: int,
        response_body: dict[str, Any],
        ttl_seconds: int | None = None,
    ) -> None:
        """Stores the response of a successful operation."""
        ttl = ttl_seconds or self.default_ttl_seconds
        now = time.time()
        self._records[idempotency_key] = IdempotencyRecord(
            key=idempotency_key,
            fingerprint=fingerprint,
            status_code=status_code,
            response_body=response_body,
            created_at=now,
            expires_at=now + ttl,
        )

    def purge_expired(self) -> int:
        """Cleans up expired records."""
        now = time.time()
        expired = [k for k, r in self._records.items() if now > r.expires_at]
        for k in expired:
            del self._records[k]
        return len(expired)

    def count(self) -> int:
        return len(self._records)


# Global singleton instance
idempotency_engine = IdempotencyEngine()
