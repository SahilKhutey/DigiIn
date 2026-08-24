"""Phase 8.8 — Privacy Controls & PII Minimization.

Implements selective disclosure and PII minimization:

  Department asks: "Is applicant income-eligible?"
  DigiIn returns:  { "income_eligible": true }
  NOT:             { "annual_income": 137500, "aadhaar": "...", "address": "..." }

Components:
  MinimalDisclosure   — returns only fields permitted for a given purpose
  PredicateEvaluator  — evaluates boolean predicates without disclosing raw values
  PIIDetector         — scans text for accidental PII and redacts it
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

# ---------------------------------------------------------------------------
# PII Detector
# ---------------------------------------------------------------------------

# Patterns for common Indian government PII
_PII_REGEXES: list[tuple[str, re.Pattern[str]]] = [
    ("aadhaar", re.compile(r"\b[2-9][0-9]{3}[\s-]?[0-9]{4}[\s-]?[0-9]{4}\b")),
    ("pan", re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")),
    ("otp", re.compile(r"\botp[\":\s]+[0-9]{4,8}\b", re.IGNORECASE)),
    ("mobile", re.compile(r"\b[6-9][0-9]{9}\b")),
    ("jwt_token", re.compile(r"eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}")),
    ("private_key", re.compile(r"-----BEGIN (RSA |EC |)PRIVATE KEY-----")),
    ("access_token", re.compile(r'"(access_token|refresh_token|api_key)"\s*:\s*"[^"]{16,}"')),
]


class PIIDetector:
    """Detects and redacts accidental PII in log entries and API responses."""

    def scan(self, text: str) -> list[str]:
        """Return list of PII types found in text."""
        found = []
        for name, pattern in _PII_REGEXES:
            if pattern.search(text):
                found.append(name)
        return found

    def contains_pii(self, text: str) -> bool:
        return bool(self.scan(text))

    def redact(self, text: str) -> str:
        """Redact all PII patterns in text."""
        result = text
        for name, pattern in _PII_REGEXES:
            result = pattern.sub(f"[REDACTED:{name.upper()}]", result)
        return result

    def redact_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Redact sensitive fields from a dict by key name heuristics."""
        _SENSITIVE_KEYS = {
            "aadhaar", "pan", "otp", "password", "secret", "token",
            "private_key", "access_token", "refresh_token", "api_key",
            "annual_income", "income", "address", "dob", "mobile", "phone",
        }
        result = {}
        for k, v in data.items():
            if k.lower() in _SENSITIVE_KEYS:
                result[k] = "[REDACTED]"
            elif isinstance(v, str) and self.contains_pii(v):
                result[k] = self.redact(v)
            elif isinstance(v, dict):
                result[k] = self.redact_dict(v)
            else:
                result[k] = v
        return result


# ---------------------------------------------------------------------------
# Disclosure purposes and field permissions
# ---------------------------------------------------------------------------


class DisclosurePurpose(StrEnum):
    INCOME_ELIGIBILITY = "income_eligibility"
    EDUCATION_VERIFICATION = "education_verification"
    DOMICILE_VERIFICATION = "domicile_verification"
    IDENTITY_VERIFICATION = "identity_verification"
    AGE_VERIFICATION = "age_verification"
    SCHOLARSHIP = "scholarship"
    ADMISSION = "admission"
    EMPLOYMENT = "employment"
    GENERAL = "general"


# Fields permitted per purpose (minimum necessary disclosure)
_PURPOSE_FIELDS: dict[DisclosurePurpose, list[str]] = {
    DisclosurePurpose.INCOME_ELIGIBILITY: ["income_eligible"],       # predicate only!
    DisclosurePurpose.EDUCATION_VERIFICATION: ["education_verified", "qualification_level", "passing_year"],
    DisclosurePurpose.DOMICILE_VERIFICATION: ["domicile_verified", "state"],
    DisclosurePurpose.IDENTITY_VERIFICATION: ["identity_verified", "name_hash"],
    DisclosurePurpose.AGE_VERIFICATION: ["age_eligible", "age_bracket"],  # not exact DOB
    DisclosurePurpose.SCHOLARSHIP: ["income_eligible", "education_verified", "domicile_verified"],
    DisclosurePurpose.ADMISSION: ["education_verified", "qualification_level", "passing_year", "percentage_bracket"],
    DisclosurePurpose.EMPLOYMENT: ["identity_verified", "education_verified"],
    DisclosurePurpose.GENERAL: ["identity_verified"],
}


# ---------------------------------------------------------------------------
# Predicate Evaluator
# ---------------------------------------------------------------------------


@dataclass
class Predicate:
    """A boolean predicate evaluated against a claim value."""

    field: str
    operator: str       # ">=", "<=", ">", "<", "==", "in"
    threshold: Any
    result_key: str     # Key name in the output (e.g. "income_eligible")


class PredicateEvaluator:
    """
    Evaluates boolean predicates against raw claim values.

    The raw value is consumed inside DigiIn and only the boolean result
    is disclosed to the requesting party.
    """

    def evaluate(self, predicate: Predicate, raw_claims: dict[str, Any]) -> dict[str, Any]:
        """Evaluate one predicate. Returns {result_key: bool}."""
        value = raw_claims.get(predicate.field)
        if value is None:
            return {predicate.result_key: False}

        satisfied = self._compare(value, predicate.operator, predicate.threshold)
        return {predicate.result_key: satisfied}

    def evaluate_all(
        self,
        predicates: list[Predicate],
        raw_claims: dict[str, Any],
    ) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for pred in predicates:
            result.update(self.evaluate(pred, raw_claims))
        return result

    def _compare(self, value: Any, operator: str, threshold: Any) -> bool:
        try:
            match operator:
                case ">=":
                    return float(value) >= float(threshold)
                case "<=":
                    return float(value) <= float(threshold)
                case ">":
                    return float(value) > float(threshold)
                case "<":
                    return float(value) < float(threshold)
                case "==":
                    return value == threshold
                case "in":
                    return value in threshold
                case _:
                    return False
        except (TypeError, ValueError):
            return False


# ---------------------------------------------------------------------------
# Minimal Disclosure Engine
# ---------------------------------------------------------------------------


class MinimalDisclosure:
    """
    Returns only the claim fields permitted for a given disclosure purpose.

    Can also evaluate predicates so that raw claim values never leave DigiIn.
    """

    def __init__(self) -> None:
        self._purpose_fields = dict(_PURPOSE_FIELDS)
        self._predicate_evaluator = PredicateEvaluator()

    def disclose(
        self,
        full_claims: dict[str, Any],
        purpose: DisclosurePurpose,
        predicates: list[Predicate] | None = None,
    ) -> dict[str, Any]:
        """
        Return only permitted fields for the purpose.

        If predicates are provided, they are evaluated against full_claims
        and their boolean results are included in the output instead of raw values.
        """
        permitted_fields = self._purpose_fields.get(purpose, ["identity_verified"])
        result: dict[str, Any] = {}

        # Evaluate predicates (raw values consumed here, not passed out)
        if predicates:
            pred_results = self._predicate_evaluator.evaluate_all(predicates, full_claims)
            for key in permitted_fields:
                if key in pred_results:
                    result[key] = pred_results[key]

        # Include pre-computed boolean/safe fields
        for field_name in permitted_fields:
            if field_name not in result and field_name in full_claims:
                result[field_name] = full_claims[field_name]

        result["purpose"] = purpose.value
        result["disclosed_at"] = __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat()
        return result

    def register_purpose(
        self, purpose: DisclosurePurpose, permitted_fields: list[str]
    ) -> None:
        """Register custom permitted fields for a disclosure purpose."""
        self._purpose_fields[purpose] = permitted_fields


# ---------------------------------------------------------------------------
# Module singletons
# ---------------------------------------------------------------------------

pii_detector = PIIDetector()
predicate_evaluator = PredicateEvaluator()
minimal_disclosure = MinimalDisclosure()
