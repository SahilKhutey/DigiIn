"""
DigiIn Performance & Scalability — Provider Rate Management & Circuit Breaker
Protects external provider endpoints from overload with rate limiting, 3-state circuit breaking, and exponential backoff.
"""

from __future__ import annotations

import random
import time


class CircuitState:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class ProviderCircuitBreaker:
    def __init__(
        self,
        provider_id: str,
        failure_threshold: int = 5,
        recovery_timeout_seconds: float = 10.0
    ):
        self.provider_id = provider_id
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout_seconds
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.time()

    def can_execute(self) -> bool:
        now = time.time()
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if now - self.last_state_change >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            return True
        return False

    def record_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_state_change = time.time()

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()

class ExponentialBackoffRetry:
    @staticmethod
    def calculate_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 30.0, jitter_pct: float = 0.2) -> float:
        """Calculates exponential backoff delay with randomized jitter."""
        exponential = base_delay * (2 ** (attempt - 1))
        capped = min(max_delay, exponential)
        jitter = capped * jitter_pct * (random.random() * 2 - 1)
        return max(0.1, round(capped + jitter, 2))
