"""
DigiIn Performance & Scalability — Distributed Rate Limiter
Implements token-bucket rate limiting multi-dimensionally across IP, user, organization, and API client.
"""

from __future__ import annotations

import time


class TokenBucket:
    def __init__(self, capacity: int, refill_rate_per_sec: float):
        self.capacity = capacity
        self.refill_rate = refill_rate_per_sec
        self.tokens = float(capacity)
        self.last_refill = time.time()

    def consume(self, amount: int = 1) -> bool:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(float(self.capacity), self.tokens + (elapsed * self.refill_rate))
        self.last_refill = now

        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False

class DistributedRateLimiter:
    def __init__(self):
        self._buckets: dict[str, TokenBucket] = {}

    def check_rate_limit(
        self,
        dimension_key: str,
        capacity: int = 100,
        refill_rate_per_sec: float = 10.0
    ) -> tuple[bool, int]:
        """Evaluates whether an entity exceeds rate limit and returns remaining tokens."""
        if dimension_key not in self._buckets:
            self._buckets[dimension_key] = TokenBucket(capacity, refill_rate_per_sec)

        bucket = self._buckets[dimension_key]
        allowed = bucket.consume(1)
        return allowed, int(bucket.tokens)
