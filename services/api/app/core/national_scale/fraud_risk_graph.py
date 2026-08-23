"""
DigiIn National Scale — Network-Wide Fraud Risk Graph Engine
Analyzes institutional verification patterns, issuer anomalies, and correlation graphs without exposing citizen PII.
"""

from __future__ import annotations

from typing import Any


class NetworkRiskGraphEngine:
    def __init__(self):
        self._issuer_patterns: dict[str, dict[str, Any]] = {}
        self._verifier_patterns: dict[str, dict[str, Any]] = {}

    def record_verification_node(self, issuer_id: str, verifier_id: str, claim_type: str, success: bool):
        if issuer_id not in self._issuer_patterns:
            self._issuer_patterns[issuer_id] = {"total": 0, "failures": 0}
        if verifier_id not in self._verifier_patterns:
            self._verifier_patterns[verifier_id] = {"total": 0, "failures": 0}

        self._issuer_patterns[issuer_id]["total"] += 1
        self._verifier_patterns[verifier_id]["total"] += 1

        if not success:
            self._issuer_patterns[issuer_id]["failures"] += 1
            self._verifier_patterns[verifier_id]["failures"] += 1

    def evaluate_risk_level(self, entity_id: str) -> tuple[str, float]:
        """Calculates risk score 0.0 to 1.0 (Low to High)."""
        pattern = self._verifier_patterns.get(entity_id) or self._issuer_patterns.get(entity_id)
        if not pattern or pattern["total"] == 0:
            return "LOW_RISK", 0.05

        failure_rate = pattern["failures"] / pattern["total"]
        if failure_rate > 0.4:
            return "HIGH_RISK", round(failure_rate, 2)
        elif failure_rate > 0.15:
            return "MODERATE_RISK", round(failure_rate, 2)
        else:
            return "LOW_RISK", round(failure_rate, 2)
