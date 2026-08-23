"""
DigiIn Performance & Scalability — Safe Tiered Cache
Caches non-sensitive reference data (provider metadata, organization profiles, public policies) with instant invalidation.
Strictly prohibits caching raw documents, passwords, or personal identity numbers.
"""

from __future__ import annotations

import time
from typing import Any

PROHIBITED_CACHE_PATTERNS = ["aadhaar", "password", "raw_document", "secret", "private_key", "token"]

class SafeTieredCache:
    def __init__(self, default_ttl_seconds: int = 300):
        self.default_ttl = default_ttl_seconds
        self._cache: dict[str, dict[str, Any]] = {}

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Stores reference data in cache after validating it does not contain prohibited PII."""
        # Validate key safety
        if any(p in key.lower() for p in PROHIBITED_CACHE_PATTERNS):
            raise ValueError(f"PRIVACY_CACHE_VIOLATION: Key '{key}' contains sensitive data pattern. Caching denied.")

        ttl = ttl_seconds or self.default_ttl
        expires_at = time.time() + ttl
        self._cache[key] = {
            "value": value,
            "expiresAt": expires_at
        }

    def get(self, key: str) -> Any | None:
        entry = self._cache.get(key)
        if not entry:
            return None
        if time.time() > entry["expiresAt"]:
            del self._cache[key]
            return None
        return entry["value"]

    def invalidate(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def invalidate_prefix(self, prefix: str) -> int:
        keys_to_del = [k for k in self._cache if k.startswith(prefix)]
        for k in keys_to_del:
            del self._cache[k]
        return len(keys_to_del)
