"""
DigiIn Provider Integration Subsystem — Provider Gateway & Orchestrator
Facade that resolves authoritative providers, applies data minimization, evaluates circuit breakers, executes retries, and normalizes evidence.
"""

from __future__ import annotations

import time
from typing import Any

from .evidence_normalizer import EvidenceNormalizer, ProviderEvidence
from .provider_adapter import (
    BoardAdapter,
    GovernmentAdapter,
    ProviderAdapter,
    ProviderVerificationRequest,
    SandboxSimulatorAdapter,
    UniversityAdapter,
)
from .provider_registry import CoreProviderRegistry


class CircuitBreakerState:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class ProviderCircuitBreaker:
    def __init__(self, failure_threshold: int = 3, reset_timeout_seconds: int = 30):
        self.failure_threshold = failure_threshold
        self.reset_timeout_seconds = reset_timeout_seconds
        self.state = CircuitBreakerState.CLOSED
        self.consecutive_failures = 0
        self.last_state_change = time.time()

    def record_success(self):
        self.consecutive_failures = 0
        self.state = CircuitBreakerState.CLOSED

    def record_failure(self):
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.last_state_change = time.time()

    def can_attempt(self, now: float | None = None) -> bool:
        current = now or time.time()
        if self.state == CircuitBreakerState.CLOSED:
            return True
        if self.state == CircuitBreakerState.OPEN:
            if current - self.last_state_change > self.reset_timeout_seconds:
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        return True  # HALF_OPEN allows single probe

class ProviderGateway:
    def __init__(self, registry: CoreProviderRegistry):
        self.registry = registry
        self._adapters: dict[str, ProviderAdapter] = {}
        self._circuit_breakers: dict[str, ProviderCircuitBreaker] = {}
        self._register_default_adapters()

    def _register_default_adapters(self):
        self.register_adapter("provider_cbse_in", BoardAdapter())
        self.register_adapter("provider_delhi_univ", UniversityAdapter())
        self.register_adapter("provider_sarathi_parivahan", GovernmentAdapter())
        self.register_adapter("provider_sandbox_sim", SandboxSimulatorAdapter())

    def register_adapter(self, provider_id: str, adapter: ProviderAdapter):
        self._adapters[provider_id] = adapter
        self._circuit_breakers[provider_id] = ProviderCircuitBreaker()

    def get_adapter(self, provider_id: str) -> ProviderAdapter | None:
        return self._adapters.get(provider_id)

    def execute_verification(
        self,
        claim_type: str,
        subject_ref: str,
        purpose: str,
        request_id: str,
        jurisdiction: str | None = None,
        parameters: dict[str, Any] | None = None,
        max_retries: int = 2
    ) -> tuple[bool, str | None, ProviderEvidence | None]:
        """
        Orchestrates authoritative provider selection, data minimization, circuit breaking, retry, and normalization.
        """
        # Step 1: Resolve capable active providers
        providers = self.registry.find_providers_for_claim(claim_type, jurisdiction)
        if not providers:
            return False, f"NO_AUTHORITATIVE_PROVIDER: No active provider found for claim '{claim_type}'.", None

        # Step 2: Attempt execution on top-priority provider
        for provider in providers:
            p_id = provider.id
            cb = self._circuit_breakers.get(p_id)
            if cb and not cb.can_attempt():
                continue  # Circuit OPEN, skip to next provider fallback

            adapter = self._adapters.get(p_id)
            if not adapter:
                continue

            # Data Minimization: Send only required parameters
            minimized_params = {
                k: v for k, v in (parameters or {}).items()
                if k in ("roll_number", "passing_year", "enrollment_no", "licence_number")
            }

            req = ProviderVerificationRequest(
                request_id=request_id,
                subject_reference=subject_ref,
                claim_types=[claim_type],
                purpose=purpose,
                correlation_id=f"corr_{request_id}",
                parameters=minimized_params
            )

            # Execution with Retry loop
            attempts = 0
            while attempts <= max_retries:
                attempts += 1
                try:
                    raw_res = adapter.verify(req)
                    if cb:
                        cb.record_success()

                    # Normalize Evidence
                    evidence = EvidenceNormalizer.normalize(
                        provider_id=p_id,
                        raw_response=raw_res.raw_body,
                        claim_type=claim_type,
                        subject_ref=subject_ref,
                        request_id=request_id
                    )
                    return True, None, evidence
                except (TimeoutError, Exception):
                    if cb:
                        cb.record_failure()
                    if attempts > max_retries:
                        break  # Fall through to fallback provider

        return False, "PROVIDER_UNAVAILABLE: Authoritative providers were unreachable or timed out.", None
