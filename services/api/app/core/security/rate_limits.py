"""Phase 8.7 — Multi-Dimension Rate Limiting.

Centralised rate-limit policies applied by multiple dimensions simultaneously:

  IP | Account | Session | Provider | API Key | Endpoint

A request is blocked if ANY configured dimension is exceeded.

Policies by endpoint group:

  Auth (login/OTP)           10 req/min    IP + Account
  Document upload             20 req/hour  Account
  Verification requests       60 req/min   Account + Purpose
  Proof verification         300 req/min   IP + API Key
  Admin operations             5 req/min   Account (always audited)
  Integration webhooks        30 req/min   Provider
  General API               120 req/min   IP
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass
from enum import StrEnum

# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------


class RateLimitDimension(StrEnum):
    IP = "ip"
    ACCOUNT = "account"
    SESSION = "session"
    PROVIDER = "provider"
    API_KEY = "api_key"
    ENDPOINT = "endpoint"


# ---------------------------------------------------------------------------
# Policy and result
# ---------------------------------------------------------------------------


@dataclass
class RateLimitPolicy:
    name: str
    max_requests: int
    window_seconds: int
    dimensions: list[RateLimitDimension]
    block_duration_seconds: int = 60        # How long to hard-block after exceed
    audit_on_exceed: bool = True


@dataclass
class RateLimitResult:
    allowed: bool
    dimension_hit: RateLimitDimension | None = None
    remaining: int = 0
    retry_after_seconds: int = 0
    policy_name: str = ""

    @property
    def headers(self) -> dict[str, str]:
        h: dict[str, str] = {"X-RateLimit-Remaining": str(self.remaining)}
        if not self.allowed:
            h["Retry-After"] = str(self.retry_after_seconds)
        return h


# ---------------------------------------------------------------------------
# Built-in policies
# ---------------------------------------------------------------------------

POLICIES: dict[str, RateLimitPolicy] = {
    "auth": RateLimitPolicy(
        name="auth",
        max_requests=10,
        window_seconds=60,
        dimensions=[RateLimitDimension.IP, RateLimitDimension.ACCOUNT],
        block_duration_seconds=300,    # 5 min block after exceed
        audit_on_exceed=True,
    ),
    "document_upload": RateLimitPolicy(
        name="document_upload",
        max_requests=20,
        window_seconds=3600,           # per hour
        dimensions=[RateLimitDimension.ACCOUNT],
        audit_on_exceed=True,
    ),
    "verification": RateLimitPolicy(
        name="verification",
        max_requests=60,
        window_seconds=60,
        dimensions=[RateLimitDimension.ACCOUNT],
        audit_on_exceed=True,
    ),
    "proof_verification": RateLimitPolicy(
        name="proof_verification",
        max_requests=300,
        window_seconds=60,
        dimensions=[RateLimitDimension.IP, RateLimitDimension.API_KEY],
        audit_on_exceed=False,
    ),
    "admin": RateLimitPolicy(
        name="admin",
        max_requests=5,
        window_seconds=60,
        dimensions=[RateLimitDimension.ACCOUNT],
        block_duration_seconds=120,
        audit_on_exceed=True,
    ),
    "webhook": RateLimitPolicy(
        name="webhook",
        max_requests=30,
        window_seconds=60,
        dimensions=[RateLimitDimension.PROVIDER, RateLimitDimension.IP],
        audit_on_exceed=True,
    ),
    "general": RateLimitPolicy(
        name="general",
        max_requests=120,
        window_seconds=60,
        dimensions=[RateLimitDimension.IP],
        audit_on_exceed=False,
    ),
}


# ---------------------------------------------------------------------------
# Multi-Dimension Rate Limiter
# ---------------------------------------------------------------------------


class _SlidingWindowCounter:
    """Sliding-window token-bucket counter per key."""

    def __init__(self) -> None:
        self._timestamps: dict[str, list[float]] = defaultdict(list)
        self._blocked_until: dict[str, float] = {}

    def check_and_record(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
        block_duration: int = 60,
    ) -> tuple[bool, int]:
        """
        Check if key is within limit and record the request.
        Returns (allowed, remaining).
        """
        now = time.monotonic()

        # Check hard block
        block_until = self._blocked_until.get(key, 0)
        if now < block_until:
            return False, 0

        # Clean old timestamps
        cutoff = now - window_seconds
        self._timestamps[key] = [t for t in self._timestamps[key] if t > cutoff]

        count = len(self._timestamps[key])
        if count >= max_requests:
            self._blocked_until[key] = now + block_duration
            return False, 0

        self._timestamps[key].append(now)
        return True, max_requests - count - 1

    def reset(self, key: str) -> None:
        self._timestamps.pop(key, None)
        self._blocked_until.pop(key, None)

    def retry_after(self, key: str, window_seconds: int) -> int:
        blocked_until = self._blocked_until.get(key, 0)
        now = time.monotonic()
        if now < blocked_until:
            return int(blocked_until - now)
        if self._timestamps.get(key):
            oldest = self._timestamps[key][0]
            return max(0, int(oldest + window_seconds - now))
        return 0


class MultiDimensionRateLimiter:
    """
    Checks rate limits across all configured dimensions for a policy.
    A request is BLOCKED if ANY dimension is exceeded.
    """

    def __init__(self) -> None:
        self._counters: dict[str, _SlidingWindowCounter] = {}
        self._policies = dict(POLICIES)

    def _counter(self, dimension: RateLimitDimension) -> _SlidingWindowCounter:
        if dimension.value not in self._counters:
            self._counters[dimension.value] = _SlidingWindowCounter()
        return self._counters[dimension.value]

    def check(
        self,
        policy_name: str,
        dimension_values: dict[RateLimitDimension, str],
    ) -> RateLimitResult:
        """
        Check all dimensions of the named policy.

        dimension_values: {RateLimitDimension.IP: "1.2.3.4", RateLimitDimension.ACCOUNT: "user-123"}
        """
        policy = self._policies.get(policy_name)
        if not policy:
            return RateLimitResult(allowed=True, remaining=999, policy_name=policy_name)

        min_remaining = policy.max_requests

        for dimension in policy.dimensions:
            dim_value = dimension_values.get(dimension)
            if not dim_value:
                continue  # Dimension not provided — skip this dimension

            key = f"{policy_name}:{dimension.value}:{dim_value}"
            counter = self._counter(dimension)
            allowed, remaining = counter.check_and_record(
                key,
                policy.max_requests,
                policy.window_seconds,
                policy.block_duration_seconds,
            )

            if not allowed:
                retry_after = counter.retry_after(key, policy.window_seconds)
                return RateLimitResult(
                    allowed=False,
                    dimension_hit=dimension,
                    remaining=0,
                    retry_after_seconds=retry_after,
                    policy_name=policy_name,
                )

            min_remaining = min(min_remaining, remaining)

        return RateLimitResult(
            allowed=True,
            remaining=min_remaining,
            policy_name=policy_name,
        )

    def reset(
        self,
        policy_name: str,
        dimension: RateLimitDimension,
        value: str,
    ) -> None:
        key = f"{policy_name}:{dimension.value}:{value}"
        self._counter(dimension).reset(key)

    def add_policy(self, policy: RateLimitPolicy) -> None:
        self._policies[policy.name] = policy


# ---------------------------------------------------------------------------
# Module singleton
# ---------------------------------------------------------------------------

rate_limiter = MultiDimensionRateLimiter()
