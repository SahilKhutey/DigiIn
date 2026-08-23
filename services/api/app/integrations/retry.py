"""Phase 7 — Retry & Idempotency.

Handles unreliable external government APIs:

  Request
    ├── success         → return result
    ├── timeout         → retry (exponential backoff)
    ├── 429 Too Many Requests → backoff + retry
    ├── 5xx Server Error      → retry up to max_attempts
    └── 4xx Client Error      → controlled failure (do NOT retry)

Idempotency keys ensure that retry storms cannot create duplicate
credentials or verification records.
"""

from __future__ import annotations

import hashlib
import json
import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Retry Policy
# ---------------------------------------------------------------------------


@dataclass
class RetryPolicy:
    """Configurable retry behaviour for a provider or operation type."""

    max_attempts: int = 3
    base_delay_s: float = 0.5       # First retry delay
    max_delay_s: float = 30.0       # Cap on exponential backoff
    jitter: bool = True             # Add random jitter to avoid thundering herd
    retryable_http_codes: set[int] = field(default_factory=lambda: {429, 500, 502, 503, 504})
    timeout_s: float = 10.0

    def delay_for_attempt(self, attempt: int) -> float:
        """Return the sleep duration for a given attempt (0-indexed)."""
        delay = min(self.base_delay_s * (2**attempt), self.max_delay_s)
        if self.jitter:
            delay *= (0.5 + random.random() * 0.5)
        return delay


# Error classification
class TransientError(RuntimeError):
    """Transient error — eligible for retry."""
    http_code: int | None = None


class PermanentError(RuntimeError):
    """Permanent 4xx error — do NOT retry."""
    http_code: int | None = None


class RateLimitError(TransientError):
    """429 Too Many Requests — wait and retry."""
    retry_after_s: float = 5.0


# ---------------------------------------------------------------------------
# Retry Runner
# ---------------------------------------------------------------------------


class RetryRunner:
    """
    Executes a callable through the retry policy.

    The callable must raise TransientError / RateLimitError for retryable
    failures and PermanentError for non-retryable failures.
    """

    def __init__(self, policy: RetryPolicy | None = None) -> None:
        self._policy = policy or RetryPolicy()

    def run(
        self,
        operation: Callable[[], T],
        operation_name: str = "external_call",
        provider_id: str = "unknown",
    ) -> T:
        last_exc: Exception | None = None
        policy = self._policy

        for attempt in range(policy.max_attempts):
            try:
                result = operation()
                if attempt > 0:
                    logger.info(
                        "Operation '%s' for provider '%s' succeeded on attempt %d",
                        operation_name, provider_id, attempt + 1,
                    )
                return result

            except RateLimitError as exc:
                last_exc = exc
                wait = exc.retry_after_s
                logger.warning(
                    "Rate limited by '%s' on '%s' (attempt %d/%d) — waiting %.1fs",
                    provider_id, operation_name, attempt + 1, policy.max_attempts, wait,
                )
                time.sleep(wait)

            except TransientError as exc:
                last_exc = exc
                if attempt + 1 >= policy.max_attempts:
                    break
                wait = policy.delay_for_attempt(attempt)
                logger.warning(
                    "Transient error from '%s' on '%s' (attempt %d/%d) — retrying in %.2fs: %s",
                    provider_id, operation_name, attempt + 1, policy.max_attempts, wait, exc,
                )
                time.sleep(wait)

            except PermanentError as exc:
                logger.error(
                    "Permanent error from '%s' on '%s': %s", provider_id, operation_name, exc
                )
                raise

        raise RuntimeError(
            f"Operation '{operation_name}' for provider '{provider_id}' failed after "
            f"{policy.max_attempts} attempts. Last error: {last_exc}"
        ) from last_exc


# ---------------------------------------------------------------------------
# Idempotency Key Generator
# ---------------------------------------------------------------------------


def make_idempotency_key(
    provider_id: str,
    operation: str,
    subject_id: str,
    content_hash: str | None = None,
) -> str:
    """
    Generate a deterministic idempotency key.

    The key is based on provider + operation + subject + content so that
    retrying the exact same request always produces the same key.
    """
    parts = [provider_id, operation, subject_id]
    if content_hash:
        parts.append(content_hash)
    raw = ":".join(parts).encode()
    return "idem-" + hashlib.sha256(raw).hexdigest()[:24]


def content_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode()
    ).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Idempotency Store (in-memory, suitable for tests and single-process dev)
# ---------------------------------------------------------------------------


@dataclass
class IdempotencyRecord:
    key: str
    operation: str
    provider_id: str
    status: str                   # "pending" | "completed" | "failed"
    result: Any | None
    created_at: datetime
    completed_at: datetime | None = None
    ttl_hours: int = 24           # Records expire after 24 hours


class IdempotencyStore:
    """
    In-memory idempotency store.

    Guarantees that an operation identified by its idempotency_key is
    executed at most once, even if the caller retries on network failure.

    In production, replace with a Redis or database-backed implementation.
    """

    def __init__(self) -> None:
        self._records: dict[str, IdempotencyRecord] = {}

    def _purge_expired(self) -> None:
        now = datetime.now(UTC)
        expired = [
            k for k, v in self._records.items()
            if now - v.created_at > timedelta(hours=v.ttl_hours)
        ]
        for k in expired:
            del self._records[k]

    def check(self, key: str) -> IdempotencyRecord | None:
        self._purge_expired()
        return self._records.get(key)

    def begin(self, key: str, operation: str, provider_id: str) -> IdempotencyRecord:
        """Reserve the key and return a 'pending' record."""
        record = IdempotencyRecord(
            key=key,
            operation=operation,
            provider_id=provider_id,
            status="pending",
            result=None,
            created_at=datetime.now(UTC),
        )
        self._records[key] = record
        return record

    def complete(self, key: str, result: Any) -> None:
        record = self._records.get(key)
        if record:
            record.status = "completed"
            record.result = result
            record.completed_at = datetime.now(UTC)

    def fail(self, key: str, error: str) -> None:
        record = self._records.get(key)
        if record:
            record.status = "failed"
            record.result = {"error": error}
            record.completed_at = datetime.now(UTC)

    def execute_once(
        self,
        key: str,
        operation: str,
        provider_id: str,
        fn: Callable[[], T],
    ) -> tuple[T, bool]:
        """
        Execute fn exactly once for the given idempotency key.

        Returns (result, was_cached) where was_cached=True means the call
        was deduplicated and the cached result was returned.
        """
        existing = self.check(key)
        if existing and existing.status == "completed":
            logger.info("Idempotency HIT for key '%s' — returning cached result", key)
            return existing.result, True  # type: ignore[return-value]

        self.begin(key, operation, provider_id)
        try:
            result = fn()
            self.complete(key, result)
            return result, False
        except Exception as exc:
            self.fail(key, str(exc))
            raise


# ---------------------------------------------------------------------------
# Module singletons
# ---------------------------------------------------------------------------

default_retry_policy = RetryPolicy()
retry_runner = RetryRunner(default_retry_policy)
idempotency_store = IdempotencyStore()
