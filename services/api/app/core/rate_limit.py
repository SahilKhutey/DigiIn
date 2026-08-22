"""Rate Limiting and Anti-Brute-Force Protection Engine."""

from __future__ import annotations

import time
from collections import defaultdict


class InMemoryRateLimiter:
    """Sliding-window token bucket rate limiter for API key, IP, and user protection."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._records: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, identifier: str) -> tuple[bool, int]:
        """Checks if request is within rate limit.

        Returns:
            (allowed: bool, remaining_requests: int)
        """
        now = time.time()
        cutoff = now - self.window_seconds

        # Clean older timestamps
        valid_timestamps = [t for t in self._records[identifier] if t > cutoff]
        self._records[identifier] = valid_timestamps

        if len(valid_timestamps) >= self.max_requests:
            return False, 0

        self._records[identifier].append(now)
        remaining = self.max_requests - len(self._records[identifier])
        return True, remaining

    def reset(self, identifier: str) -> None:
        if identifier in self._records:
            del self._records[identifier]


auth_rate_limiter = InMemoryRateLimiter(max_requests=10, window_seconds=60)
api_rate_limiter = InMemoryRateLimiter(max_requests=120, window_seconds=60)
