"""
DigiIn Controlled Pilot & Production Validation — 5-Dimension Go / No-Go Launch Gate
Evaluates Security, Privacy, Reliability, UX, and Operations readiness before authorizing general production traffic ramp.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


class TrafficRampStage:
    STAGE_1 = 5
    STAGE_2 = 15
    STAGE_3 = 30
    STAGE_4 = 60
    STAGE_5_GA = 100

@dataclass
class GateEvaluationDimension:
    dimension: str  # "SECURITY" | "PRIVACY" | "RELIABILITY" | "UX" | "OPERATIONS"
    passed: bool
    evidence_notes: str
    evaluated_by: str
    evaluated_at: float = field(default_factory=time.time)

class ProductionGoNoGoGate:
    def __init__(self):
        self._dimensions: dict[str, GateEvaluationDimension] = {}
        self._current_traffic_percentage = 0
        self._is_launch_approved = False

    def record_dimension_evaluation(
        self,
        dimension: str,
        passed: bool,
        notes: str,
        evaluator: str
    ) -> GateEvaluationDimension:
        dim = GateEvaluationDimension(
            dimension=dimension,
            passed=passed,
            evidence_notes=notes,
            evaluated_by=evaluator
        )
        self._dimensions[dimension] = dim
        return dim

    def evaluate_overall_readiness(self) -> tuple[bool, dict[str, Any]]:
        required = ["SECURITY", "PRIVACY", "RELIABILITY", "UX", "OPERATIONS"]
        results = {}
        all_passed = True

        for req in required:
            dim = self._dimensions.get(req)
            if not dim or not dim.passed:
                results[req] = "FAIL" if dim else "NOT_EVALUATED"
                all_passed = False
            else:
                results[req] = "PASS"

        self._is_launch_approved = all_passed
        decision = "GO" if all_passed else "NO_GO"
        return all_passed, {
            "decision": decision,
            "dimensions": results,
            "canRampTraffic": all_passed,
        }

    def ramp_traffic(self, target_percentage: int) -> tuple[bool, str, int]:
        if not self._is_launch_approved:
            return False, "RAMP_DENIED: Go/No-Go gate has not approved general production readiness.", self._current_traffic_percentage

        if target_percentage not in (TrafficRampStage.STAGE_1, TrafficRampStage.STAGE_2, TrafficRampStage.STAGE_3, TrafficRampStage.STAGE_4, TrafficRampStage.STAGE_5_GA):
            return False, f"INVALID_STAGE: Target {target_percentage}% is not an authorized ramp stage.", self._current_traffic_percentage

        self._current_traffic_percentage = target_percentage
        return True, f"TRAFFIC_RAMPED_TO_{target_percentage}_PERCENT", self._current_traffic_percentage
