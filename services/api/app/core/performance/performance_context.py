"""
DigiIn Performance & Scalability — Performance Context & Dependency Timing
Measures granular latency across pipeline stages (Auth, Policy, Database, Provider, Serialization) without capturing sensitive PII.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PerformanceContext:
    request_id: str
    operation: str
    started_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    actor_type: str | None = None
    organization_id: str | None = None
    dependency_timings: dict[str, float] = field(default_factory=dict)
    _active_stage_start: float | None = None
    _active_stage_name: str | None = None

    def start_stage(self, stage_name: str):
        self._active_stage_name = stage_name
        self._active_stage_start = time.perf_counter()

    def end_stage(self, stage_name: str | None = None):
        if not self._active_stage_start:
            return
        target = stage_name or self._active_stage_name or "unknown"
        elapsed_ms = round((time.perf_counter() - self._active_stage_start) * 1000.0, 2)
        self.dependency_timings[target] = self.dependency_timings.get(target, 0.0) + elapsed_ms
        self._active_stage_start = None
        self._active_stage_name = None

    def finalize(self) -> dict[str, Any]:
        self.completed_at = time.time()
        total_duration_ms = round((self.completed_at - self.started_at) * 1000.0, 2)
        return {
            "requestId": self.request_id,
            "operation": self.operation,
            "totalDurationMs": total_duration_ms,
            "timings": self.dependency_timings,
            "actorType": self.actor_type,
            "organizationId": self.organization_id,
        }

class DependencyTimer:
    @staticmethod
    def create_context(operation: str, actor_type: str | None = None, org_id: str | None = None) -> PerformanceContext:
        req_id = f"req_{secrets.token_hex(8)}"
        return PerformanceContext(
            request_id=req_id,
            operation=operation,
            actor_type=actor_type,
            organization_id=org_id
        )
