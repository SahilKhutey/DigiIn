"""
DigiIn Performance & Scalability — Idempotency Engine
Prevents double-execution of critical verification requests or proof minting during network retries.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any


class IdempotencyRecord:
    def __init__(self, key: str, request_hash: str, response_payload: dict[str, Any], ttl_seconds: int = 86400):
        self.key = key
        self.request_hash = request_hash
        self.response_payload = response_payload
        self.created_at = time.time()
        self.expires_at = self.created_at + ttl_seconds

class IdempotencyEngine:
    def __init__(self):
        self._cache: dict[str, IdempotencyRecord] = {}

    @staticmethod
    def compute_request_hash(payload: dict[str, Any]) -> str:
        serialized = str(sorted(payload.items()))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def process_idempotent_request(
        self,
        idempotency_key: str,
        request_payload: dict[str, Any]
    ) -> tuple[bool, dict[str, Any] | None]:
        """
        Returns (is_cache_hit, cached_response).
        If hit, caller should return cached_response immediately without re-executing business logic.
        """
        req_hash = self.compute_request_hash(request_payload)
        record = self._cache.get(idempotency_key)

        if record:
            if time.time() > record.expires_at:
                del self._cache[idempotency_key]
            elif record.request_hash == req_hash:
                return True, record.response_payload
            else:
                # Key reused with different payload -> CONFLICT
                raise ValueError("IDEMPOTENCY_KEY_REUSE_PAYLOAD_MISMATCH: Key used with conflicting request body.")

        return False, None

    def store_response(
        self,
        idempotency_key: str,
        request_payload: dict[str, Any],
        response_payload: dict[str, Any],
        ttl_seconds: int = 86400
    ) -> None:
        req_hash = self.compute_request_hash(request_payload)
        self._cache[idempotency_key] = IdempotencyRecord(
            key=idempotency_key,
            request_hash=req_hash,
            response_payload=response_payload,
            ttl_seconds=ttl_seconds
        )
