"""
DigiIn Observability Subsystem — Liveness & Readiness Probes
Provides Kubernetes/Docker production probes distinguishing process health from dependency readiness.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class HealthProbeManager:
    def __init__(self):
        self._readiness_checks: dict[str, Callable[[], bool]] = {}
        self._seed_default_checks()

    def _seed_default_checks(self):
        # Default mock healthy dependency checks
        self.register_check("database", lambda: True)
        self.register_check("queue", lambda: True)
        self.register_check("storage", lambda: True)
        self.register_check("provider_gateway", lambda: True)
        self.register_check("key_manager", lambda: True)

    def register_check(self, name: str, check_fn: Callable[[], bool]):
        self._readiness_checks[name] = check_fn

    def check_liveness(self) -> dict[str, Any]:
        """Liveness check: returns 200 alive if process is functioning."""
        return {
            "status": "alive",
            "service": "digiin-api",
            "process": "ok",
        }

    def check_readiness(self) -> dict[str, Any]:
        """Readiness check: evaluates all critical backend dependencies."""
        dep_results = {}
        all_ready = True
        for name, fn in self._readiness_checks.items():
            try:
                healthy = fn()
                dep_results[name] = "healthy" if healthy else "unhealthy"
                if not healthy:
                    all_ready = False
            except Exception:
                dep_results[name] = "error"
                all_ready = False

        return {
            "status": "ready" if all_ready else "degraded",
            "service": "digiin-api",
            "dependencies": dep_results,
        }
