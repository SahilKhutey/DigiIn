"""
DigiIn Performance & Scalability — Performance Budgets & Regression Evaluator
Compares release latency measurements against established SLO performance budgets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PerformanceBudget:
    metric_name: str
    target_p95_ms: float
    target_p99_ms: float

class PerformanceBudgetEvaluator:
    def __init__(self):
        self._budgets: dict[str, PerformanceBudget] = {
            "api_overall": PerformanceBudget("api_overall", target_p95_ms=500.0, target_p99_ms=1000.0),
            "auth_endpoint": PerformanceBudget("auth_endpoint", target_p95_ms=400.0, target_p99_ms=800.0),
            "metadata_lookup": PerformanceBudget("metadata_lookup", target_p95_ms=300.0, target_p99_ms=600.0),
            "db_query": PerformanceBudget("db_query", target_p95_ms=100.0, target_p99_ms=250.0),
            "queue_enqueue": PerformanceBudget("queue_enqueue", target_p95_ms=100.0, target_p99_ms=200.0),
        }

    def evaluate_metric(self, metric_name: str, actual_p95_ms: float, actual_p99_ms: float) -> tuple[bool, dict[str, Any]]:
        budget = self._budgets.get(metric_name)
        if not budget:
            return True, {"status": "NO_BUDGET_DEFINED"}

        p95_passed = actual_p95_ms <= budget.target_p95_ms
        p99_passed = actual_p99_ms <= budget.target_p99_ms
        passed = p95_passed and p99_passed

        return passed, {
            "metric": metric_name,
            "passed": passed,
            "p95": {"actual": actual_p95_ms, "target": budget.target_p95_ms, "passed": p95_passed},
            "p99": {"actual": actual_p99_ms, "target": budget.target_p99_ms, "passed": p99_passed},
        }
