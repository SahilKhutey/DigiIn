"""
DigiIn Observability Subsystem — Platform Metrics Collector
Records counters, latencies, error rates, and calculates operational percentiles (p50, p95, p99).
"""

from __future__ import annotations

import math
from typing import Any


class MetricsCollector:
    def __init__(self):
        self._counters: dict[str, int] = {}
        self._latencies: dict[str, list[float]] = {}
        self._gauges: dict[str, float] = {}

    def increment_counter(self, name: str, amount: int = 1):
        self._counters[name] = self._counters.get(name, 0) + amount

    def get_counter(self, name: str) -> int:
        return self._counters.get(name, 0)

    def record_latency(self, metric_name: str, latency_ms: float):
        self._latencies.setdefault(metric_name, []).append(latency_ms)

    def set_gauge(self, name: str, value: float):
        self._gauges[name] = value

    def get_gauge(self, name: str) -> float:
        return self._gauges.get(name, 0.0)

    def calculate_percentiles(self, metric_name: str) -> dict[str, float]:
        values = self._latencies.get(metric_name, [])
        if not values:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "count": 0, "avg": 0.0}

        sorted_vals = sorted(values)
        n = len(sorted_vals)
        p50_idx = int(math.ceil(0.50 * n)) - 1
        p95_idx = int(math.ceil(0.95 * n)) - 1
        p99_idx = int(math.ceil(0.99 * n)) - 1

        return {
            "p50": round(sorted_vals[max(0, p50_idx)], 2),
            "p95": round(sorted_vals[max(0, p95_idx)], 2),
            "p99": round(sorted_vals[max(0, p99_idx)], 2),
            "count": n,
            "avg": round(sum(sorted_vals) / n, 2),
        }

    def get_summary(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "latencies": {k: self.calculate_percentiles(k) for k in self._latencies},
        }
