"""
DigiIn Developer Platform — Usage Metering & Rate Limiting
Tracks API invocations, response statuses, latencies, and enforces configurable per-application quotas.
"""

from __future__ import annotations

import time
from typing import Any

from .models import ApiUsageRecord


class UsageMeterService:
    def __init__(self, requests_per_minute_limit: int = 120):
        self.rpm_limit = requests_per_minute_limit
        self._records: list[ApiUsageRecord] = []
        self._app_timestamps: dict[str, list[float]] = {}

    def check_rate_limit(self, application_id: str, now: float | None = None) -> bool:
        """Enforces sliding window rate limit per application."""
        current = now or time.time()
        window_start = current - 60.0

        timestamps = self._app_timestamps.setdefault(application_id, [])
        # Prune older than 60s
        self._app_timestamps[application_id] = [t for t in timestamps if t > window_start]

        if len(self._app_timestamps[application_id]) >= self.rpm_limit:
            return False

        self._app_timestamps[application_id].append(current)
        return True

    def record_usage(self, application_id: str, endpoint: str, status_code: int, latency_ms: float):
        rec = ApiUsageRecord(
            application_id=application_id,
            endpoint=endpoint,
            status_code=status_code,
            latency_ms=latency_ms
        )
        self._records.append(rec)

    def get_application_metrics(self, application_id: str) -> dict[str, Any]:
        app_records = [r for r in self._records if r.application_id == application_id]
        total = len(app_records)
        if total == 0:
            return {"totalRequests": 0, "successRate": 100.0, "avgLatencyMs": 0.0}

        successes = sum(1 for r in app_records if 200 <= r.status_code < 300)
        avg_lat = sum(r.latency_ms for r in app_records) / total
        return {
            "totalRequests": total,
            "successRate": round((successes / total) * 100.0, 2),
            "avgLatencyMs": round(avg_lat, 2)
        }
