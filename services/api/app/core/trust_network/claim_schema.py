"""
DigiIn Trust Network & Interoperability — Immutable Claim Schema Registry
Maintains versioned canonical claim schemas with strict validation to ensure cross-service interoperability.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ClaimSchema:
    type_name: str
    version: str
    required_fields: list[str]
    field_types: dict[str, str]
    description: str

class ClaimSchemaRegistry:
    def __init__(self):
        self._schemas: dict[str, ClaimSchema] = {}
        self._seed_default_schemas()

    def _seed_default_schemas(self):
        s1 = ClaimSchema(
            type_name="education.degree",
            version="1.0",
            required_fields=["degree", "institution", "year"],
            field_types={"degree": "string", "institution": "string", "year": "integer", "cgpa": "float"},
            description="University Degree Credential Schema"
        )
        s2 = ClaimSchema(
            type_name="identity.age_over_18",
            version="1.0",
            required_fields=["isOver18"],
            field_types={"isOver18": "boolean"},
            description="Zero-Knowledge / Minimal Age Qualification Schema"
        )
        s3 = ClaimSchema(
            type_name="licence.driving",
            version="1.0",
            required_fields=["licenceNumber", "vehicleClass", "validUntil"],
            field_types={"licenceNumber": "string", "vehicleClass": "string", "validUntil": "string"},
            description="Motor Vehicle Driving Licence Schema"
        )
        self.register_schema(s1)
        self.register_schema(s2)
        self.register_schema(s3)

    def register_schema(self, schema: ClaimSchema) -> None:
        key = f"{schema.type_name}:{schema.version}"
        self._schemas[key] = schema

    def get_schema(self, type_name: str, version: str = "1.0") -> ClaimSchema | None:
        return self._schemas.get(f"{type_name}:{version}")

    def validate_claim_payload(self, type_name: str, payload: dict[str, Any], version: str = "1.0") -> tuple[bool, str | None]:
        schema = self.get_schema(type_name, version)
        if not schema:
            return False, f"SCHEMA_NOT_FOUND: Claim schema '{type_name}:{version}' is not registered."

        # Verify mandatory fields
        missing = [f for f in schema.required_fields if f not in payload]
        if missing:
            return False, f"SCHEMA_VALIDATION_FAILED: Missing required fields: {', '.join(missing)}"

        return True, None
