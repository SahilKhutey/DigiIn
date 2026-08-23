"""
DigiIn Long-Term Infrastructure — Universal Claim Registry
Enforces standard claim naming taxonomy (<domain>.<claim>) and versioned field schemas.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

CLAIM_NAMESPACE_PATTERN = re.compile(r"^[a-z0-9_]+\.[a-z0-9_]+$")

@dataclass
class UniversalClaimSchema:
    namespace_type: str  # e.g., "education.degree"
    version: str
    required_fields: list[str]
    assurance_profile: str  # "A1_BASIC" to "A4_REGULATED"
    status: str = "ACTIVE"

class UniversalClaimRegistry:
    def __init__(self):
        self._schemas: dict[str, UniversalClaimSchema] = {}
        self._seed_default_schemas()

    def _seed_default_schemas(self):
        self.register_schema(
            namespace_type="education.degree",
            version="1.0.0",
            required_fields=["degree", "institution", "year"],
            assurance_profile="A3_HIGH_ASSURANCE"
        )
        self.register_schema(
            namespace_type="identity.name",
            version="1.0.0",
            required_fields=["full_name"],
            assurance_profile="A4_REGULATED"
        )
        self.register_schema(
            namespace_type="employment.status",
            version="1.0.0",
            required_fields=["employer", "status"],
            assurance_profile="A2_VERIFIED_ORG"
        )
        self.register_schema(
            namespace_type="licence.driving",
            version="1.0.0",
            required_fields=["licence_number", "vehicle_classes"],
            assurance_profile="A4_REGULATED"
        )

    def register_schema(
        self,
        namespace_type: str,
        version: str,
        required_fields: list[str],
        assurance_profile: str
    ) -> UniversalClaimSchema:
        if not CLAIM_NAMESPACE_PATTERN.match(namespace_type):
            raise ValueError(f"INVALID_CLAIM_NAMESPACE: '{namespace_type}' does not follow <domain>.<claim> convention.")

        key = f"{namespace_type}:{version}"
        schema = UniversalClaimSchema(
            namespace_type=namespace_type,
            version=version,
            required_fields=required_fields,
            assurance_profile=assurance_profile,
            status="ACTIVE"
        )
        self._schemas[key] = schema
        return schema

    def validate_claim_payload(self, namespace_type: str, version: str, payload: dict[str, Any]) -> tuple[bool, str | None]:
        key = f"{namespace_type}:{version}"
        schema = self._schemas.get(key)
        if not schema:
            return False, f"SCHEMA_NOT_FOUND: {key}"

        missing = [f for f in schema.required_fields if f not in payload]
        if missing:
            return False, f"SCHEMA_VALIDATION_FAILED: Missing fields {missing}"

        return True, None
