"""Phase 7 — Response Normalizer.

External government APIs return wildly different field names and value
formats.  This module normalizes any raw external response into DigiIn's
own canonical domain types so the credential engine never depends on
an external API's naming conventions.

Example:
    Department A:   {"resident": true, "district": "Raipur"}
    Department B:   {"domicileStatus": "VALID", "districtCode": "RPR"}
    DigiIn output:  {"claim_type": "domicile", "status": "verified",
                     "source": "...", "verified_at": "...",
                     "evidence_reference": "..."}
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Normalization Rule
# ---------------------------------------------------------------------------


@dataclass
class NormalizationRule:
    """Maps a provider-specific field key to a DigiIn canonical field key."""

    provider_id: str
    claim_type: str
    field_mappings: dict[str, str]  # external_key → digiin_canonical_key
    status_map: dict[str, str]      # external_status_value → digiin_status
    status_field: str = "status"    # the field holding the status in external response


# ---------------------------------------------------------------------------
# Canonical DigiIn field names
# ---------------------------------------------------------------------------

CANONICAL = {
    "candidate_name": "candidate_name",
    "district": "district",
    "state": "state",
    "income": "annual_income",
    "year": "passing_year",
    "roll": "document_number",
}

# Resident / domicile status vocabulary
_TRUTHY_STATUS = {"true", "1", "valid", "yes", "active", "verified", "resident", "pass", "present"}


def _normalize_status(raw: Any) -> str:
    if isinstance(raw, bool):
        return "verified" if raw else "rejected"
    return "verified" if str(raw).lower() in _TRUTHY_STATUS else "rejected"


# ---------------------------------------------------------------------------
# Built-in normalization rules per provider
# ---------------------------------------------------------------------------

_DEFAULT_RULES: list[NormalizationRule] = [
    NormalizationRule(
        provider_id="mock-cbse-001",
        claim_type="education",
        field_mappings={
            "qualification": "qualification",
            "board": "issuer_name",
            "passing_year": "passing_year",
            "result": "result",
            "stream": "stream",
            "roll_number": "document_number",
        },
        status_map={"PASS": "verified", "FAIL": "rejected", "WITHHELD": "pending"},
        status_field="result",
    ),
    NormalizationRule(
        provider_id="mock-revenue-001",
        claim_type="domicile",
        field_mappings={
            "resident": "is_resident",
            "district": "district",
            "districtCode": "district_code",
            "domicileStatus": "domicile_status",
        },
        status_map={"VALID": "verified", "INVALID": "rejected"},
        status_field="domicileStatus",
    ),
    NormalizationRule(
        provider_id="mock-revenue-income",
        claim_type="income",
        field_mappings={
            "annual_income_inr": "annual_income",
            "category": "income_category",
        },
        status_map={"CONFIRMED": "verified"},
        status_field="status",
    ),
    NormalizationRule(
        provider_id="mock-transport-001",
        claim_type="driving_license",
        field_mappings={
            "license_number": "document_number",
            "validity": "valid_until",
            "class": "vehicle_class",
        },
        status_map={"ACTIVE": "verified", "EXPIRED": "rejected", "SUSPENDED": "rejected"},
        status_field="license_status",
    ),
]


class NormalizationRuleRegistry:
    def __init__(self) -> None:
        self._rules: dict[str, NormalizationRule] = {}
        for rule in _DEFAULT_RULES:
            self.register(rule)

    def register(self, rule: NormalizationRule) -> None:
        key = f"{rule.provider_id}:{rule.claim_type}"
        self._rules[key] = rule

    def get(self, provider_id: str, claim_type: str) -> NormalizationRule | None:
        return self._rules.get(f"{provider_id}:{claim_type}")


# ---------------------------------------------------------------------------
# Normalizer
# ---------------------------------------------------------------------------


class ExternalResponseNormalizer:
    """
    Transforms raw external API responses into DigiIn canonical domain objects.

    The normalizer is the last firewall before external data enters DigiIn.
    Any field not listed in the normalization rule is dropped.
    """

    def __init__(self, rule_registry: NormalizationRuleRegistry | None = None) -> None:
        self._registry = rule_registry or NormalizationRuleRegistry()

    def normalize(
        self,
        provider_id: str,
        claim_type: str,
        raw_response: dict[str, Any],
        request_id: str,
        simulated: bool = False,
    ) -> dict[str, Any]:
        rule = self._registry.get(provider_id, claim_type)
        normalized: dict[str, Any] = {}

        if rule:
            # Map only known external fields → canonical keys
            for ext_key, canonical_key in rule.field_mappings.items():
                if ext_key in raw_response:
                    normalized[canonical_key] = raw_response[ext_key]

            # Resolve status
            raw_status = raw_response.get(rule.status_field)
            if raw_status is not None:
                status = rule.status_map.get(str(raw_status), _normalize_status(raw_status))
            else:
                status = "verified"  # Default for mock/dev providers with no status field
        else:
            # Generic fallback normalization — lowercase all keys
            logger.warning(
                "No normalization rule for provider='%s' claim_type='%s'; using generic fallback.",
                provider_id,
                claim_type,
            )
            normalized = {k.lower().replace(" ", "_"): v for k, v in raw_response.items()}
            status = _normalize_status(raw_response.get("status", True))

        # Build DigiIn evidence reference (deterministic hash, not raw data)
        content = json.dumps(normalized, sort_keys=True, default=str).encode()
        evidence_ref = f"ev-{hashlib.sha256(content).hexdigest()[:16]}"

        return {
            "claim_type": claim_type,
            "status": status,
            "source": provider_id + ("-simulated" if simulated else ""),
            "verified_at": datetime.now(UTC).isoformat(),
            "evidence_reference": evidence_ref,
            "normalized_claims": normalized,
            "simulated": simulated,
        }


# ---------------------------------------------------------------------------
# Module singletons
# ---------------------------------------------------------------------------

rule_registry = NormalizationRuleRegistry()
normalizer = ExternalResponseNormalizer(rule_registry)
