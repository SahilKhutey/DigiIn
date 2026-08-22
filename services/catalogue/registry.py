"""Document Catalogue & Credential Schema Registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SchemaAttribute:
    name: str
    label: str
    data_type: str  # "string", "number", "date", "boolean"
    required: bool = True
    maskable: bool = True
    zk_supported_operators: list[str] = field(default_factory=lambda: ["EQUALS"])


@dataclass
class CredentialSchemaDefinition:
    schema_id: str
    title: str
    category: str
    primary_issuer: str
    authority_level: int
    attributes: list[SchemaAttribute]
    description: str


STANDARD_SCHEMAS: dict[str, CredentialSchemaDefinition] = {
    "CLASS_XII": CredentialSchemaDefinition(
        schema_id="CLASS_XII",
        title="Senior School Certificate (Class XII)",
        category="EDUCATION",
        primary_issuer="CBSE (Central Board of Secondary Education)",
        authority_level=4,
        attributes=[
            SchemaAttribute(name="student_name", label="Candidate Full Name", data_type="string", required=True, maskable=False),
            SchemaAttribute(name="roll_number", label="Roll Number", data_type="string", required=True, maskable=False),
            SchemaAttribute(name="passing_year", label="Passing Year", data_type="number", required=True, maskable=True, zk_supported_operators=["EQUALS", "GTE", "LTE", "BETWEEN"]),
            SchemaAttribute(name="percentage", label="Aggregate Score (%)", data_type="number", required=True, maskable=True, zk_supported_operators=["GTE", "LTE", "GT", "LT", "BETWEEN"]),
            SchemaAttribute(name="board", label="Examination Board", data_type="string", required=True, maskable=True, zk_supported_operators=["EQUALS", "IN"]),
        ],
        description="Authoritative secondary school completion credential issued by CBSE and State Secondary Boards.",
    ),
    "LAND_RECORD": CredentialSchemaDefinition(
        schema_id="LAND_RECORD",
        title="Khasra / Agricultural Land Title Record",
        category="REVENUE",
        primary_issuer="State Land Records & Revenue Department",
        authority_level=4,
        attributes=[
            SchemaAttribute(name="recorded_owner", label="Recorded Title Holder", data_type="string", required=True, maskable=False),
            SchemaAttribute(name="survey_number", label="Survey / Khasra No.", data_type="string", required=True, maskable=False),
            SchemaAttribute(name="area_hectares", label="Total Land Area (Hectares)", data_type="number", required=True, maskable=True, zk_supported_operators=["GTE", "LTE"]),
            SchemaAttribute(name="district", label="District Jurisdiction", data_type="string", required=True, maskable=True, zk_supported_operators=["EQUALS", "IN"]),
            SchemaAttribute(name="land_use_type", label="Permitted Land Use", data_type="string", required=True, maskable=True, zk_supported_operators=["EQUALS", "IN"]),
        ],
        description="Official real property and agricultural title ownership certificate.",
    ),
    "DRIVING_LICENCE": CredentialSchemaDefinition(
        schema_id="DRIVING_LICENCE",
        title="Motor Vehicle Driving Licence",
        category="TRANSPORT",
        primary_issuer="MoRTH / Sarathi National Transport Authority",
        authority_level=4,
        attributes=[
            SchemaAttribute(name="holder_name", label="Licence Holder Name", data_type="string", required=True, maskable=False),
            SchemaAttribute(name="licence_number", label="Licence Number", data_type="string", required=True, maskable=False),
            SchemaAttribute(name="vehicle_classes", label="Authorized Vehicle Classes", data_type="string", required=True, maskable=True, zk_supported_operators=["IN", "EXISTS"]),
            SchemaAttribute(name="valid_till", label="Validity Expiration Date", data_type="date", required=True, maskable=True, zk_supported_operators=["GTE"]),
            SchemaAttribute(name="rto_jurisdiction", label="Issuing RTO", data_type="string", required=True, maskable=True, zk_supported_operators=["EQUALS", "IN"]),
        ],
        description="Official motor vehicle driving licence recognized across all Indian states and Union Territories.",
    ),
}


class CatalogueService:
    """Provides schema lookup and validation against registered credential standards."""

    def get_schema(self, schema_id: str) -> CredentialSchemaDefinition | None:
        return STANDARD_SCHEMAS.get(schema_id.upper())

    def list_schemas(self, category: str | None = None) -> list[CredentialSchemaDefinition]:
        if category:
            return [s for s in STANDARD_SCHEMAS.values() if s.category.upper() == category.upper()]
        return list(STANDARD_SCHEMAS.values())

    def validate_claims_against_schema(self, schema_id: str, claims: dict[str, Any]) -> tuple[bool, list[str]]:
        schema = self.get_schema(schema_id)
        if not schema:
            return False, [f"Unknown credential schema: {schema_id}"]

        errors = []
        for attr in schema.attributes:
            if attr.required and attr.name not in claims:
                errors.append(f"Missing required claim attribute: {attr.name}")

        return len(errors) == 0, errors


catalogue_service = CatalogueService()
