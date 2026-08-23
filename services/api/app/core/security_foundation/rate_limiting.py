"""
DigiIn Core Security Subsystem — Tiered Rate Limiting & Anti-Abuse
Implements token bucket rate limits customized across sensitive endpoints.
"""

import time

# Tiered Limits: (max_requests, window_seconds)
RATE_LIMIT_TIERS = {
    "LOGIN": (5, 60),          # Strict: 5 requests / min
    "OTP": (3, 60),            # Very Strict: 3 requests / min
    "UPLOAD": (10, 60),        # Moderate: 10 uploads / min
    "VERIFICATION": (30, 60),  # Moderate: 30 requests / min
    "PROOF_VERIFY": (120, 60), # High: 120 verifications / min
    "PUBLIC_HEALTH": (300, 60),# High: 300 checks / min
    "ADMIN_API": (20, 60),     # Strict: 20 admin actions / min
}

class RateLimiterService:
    def __init__(self):
        self._buckets: dict[str, list] = {}

    def check_rate_limit(self, client_key: str, tier: str = "VERIFICATION") -> tuple[bool, int, int | None]:
        """
        Check and record request against configured rate limit tier.
        Returns: (allowed: bool, remaining_tokens: int, retry_after_seconds: Optional[int])
        """
        max_requests, window_seconds = RATE_LIMIT_TIERS.get(tier, (60, 60))
        now = time.time()
        bucket_key = f"{tier}:{client_key}"

        timestamps = self._buckets.setdefault(bucket_key, [])
        # Prune expired timestamps
        valid_timestamps = [t for t in timestamps if now - t < window_seconds]
        self._buckets[bucket_key] = valid_timestamps

        if len(valid_timestamps) >= max_requests:
            oldest_timestamp = valid_timestamps[0]
            retry_after = int(window_seconds - (now - oldest_timestamp)) + 1
            return False, 0, max(retry_after, 1)

        valid_timestamps.append(now)
        remaining = max_requests - len(valid_timestamps)
        return True, remaining, None

    def reset_bucket(self, client_key: str, tier: str) -> None:
        bucket_key = f"{tier}:{client_key}"
        self._buckets.pop(bucket_key, None)
