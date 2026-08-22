"""Verification rules and policy definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MatchingRule:
    field_name: str
    weight: float
    fuzzy: bool = False
    tolerance: float = 0.0


EDUCATION_MATCHING_RULES = [
    MatchingRule(field_name="roll_number", weight=0.4, fuzzy=False),
    MatchingRule(field_name="student_name", weight=0.3, fuzzy=True, tolerance=0.85),
    MatchingRule(field_name="passing_year", weight=0.2, fuzzy=False),
    MatchingRule(field_name="board", weight=0.1, fuzzy=True, tolerance=0.9),
]


def score_evidence_match(citizen_data: dict[str, Any], registry_data: dict[str, Any]) -> float:
    """Calculate demographic and document claim match score (0.0 to 100.0)."""
    total_score = 0.0
    for rule in EDUCATION_MATCHING_RULES:
        c_val = str(citizen_data.get(rule.field_name, "")).strip().lower()
        r_val = str(registry_data.get(rule.field_name, "")).strip().lower()
        if not c_val or not r_val:
            continue
        if c_val == r_val:
            total_score += rule.weight * 100.0
        elif rule.fuzzy and (c_val in r_val or r_val in c_val):
            total_score += rule.weight * 80.0
    return min(100.0, total_score)
