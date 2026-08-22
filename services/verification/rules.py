"""Verification rules and zero-knowledge predicate evaluation definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MatchingRule:
    field_name: str
    weight: float
    fuzzy: bool = False
    tolerance: float = 0.0


@dataclass
class PredicateRule:
    attribute: str
    operator: str  # "GTE", "LTE", "EQUALS", "IN", "EXISTS", "BETWEEN"
    value: Any
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


def evaluate_predicate_condition(rule: PredicateRule, attributes: dict[str, Any]) -> bool:
    """Evaluate a zero-knowledge predicate assertion without exposing underlying sensitive raw values."""
    actual = attributes.get(rule.attribute)
    if actual is None:
        return False

    op = rule.operator.upper()
    try:
        if op in ["GTE", ">="]:
            return float(actual) >= float(rule.value)
        elif op in ["LTE", "<="]:
            return float(actual) <= float(rule.value)
        elif op in ["GT", ">"]:
            return float(actual) > float(rule.value)
        elif op in ["LT", "<"]:
            return float(actual) < float(rule.value)
        elif op in ["EQUALS", "EQ", "=="]:
            return str(actual).strip().upper() == str(rule.value).strip().upper()
        elif op in ["IN", "IN_SET"]:
            val_set = [str(x).strip().upper() for x in (rule.value if isinstance(rule.value, list) else [rule.value])]
            return str(actual).strip().upper() in val_set
        elif op == "BETWEEN" and isinstance(rule.value, (list, tuple)) and len(rule.value) == 2:
            return float(rule.value[0]) <= float(actual) <= float(rule.value[1])
        elif op == "EXISTS":
            return actual is not None and str(actual).strip() != ""
    except (ValueError, TypeError):
        return False

    return False
