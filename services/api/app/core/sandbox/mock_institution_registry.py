"""
DigiIn Production-Style Hackathon Mock-Institution Framework.

Architecture:
  Institution (e.g. EDU-DEMO-001)
     └── Services (e.g. EDU-SCHOLARSHIP-DEMO)
           └── Standardized Scopes (e.g. education.qualification, income.status, domicile.status)
                 └── Verification Requests (VR-XXXXXX)
                       └── Citizen Consent
                             └── Cryptographically Signed Assertion (VA-XXXXXX)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.core.verification_layer import verification_layer


@dataclass
class VerificationScopeDefinition:
    """Standardized verification scope definition."""

    scope_code: str
    display_name: str
    description: str
    category: str


# Canonical Registry of Standardized Scopes
STANDARDIZED_SCOPES: dict[str, VerificationScopeDefinition] = {
    "identity.basic": VerificationScopeDefinition(
        scope_code="identity.basic",
        display_name="Basic Identity Assertion",
        description="Full legal name and sovereign identity confirmation",
        category="Identity",
    ),
    "identity.address": VerificationScopeDefinition(
        scope_code="identity.address",
        display_name="State Residence & Address",
        description="Permanent residential address verification",
        category="Identity",
    ),
    "education.status": VerificationScopeDefinition(
        scope_code="education.status",
        display_name="Educational Enrollment Status",
        description="Active student or graduate enrollment record",
        category="Education",
    ),
    "education.qualification": VerificationScopeDefinition(
        scope_code="education.qualification",
        display_name="Class XII Qualification & Marks",
        description="Senior secondary board marksheet and percentage",
        category="Education",
    ),
    "income.status": VerificationScopeDefinition(
        scope_code="income.status",
        display_name="Annual Household Income Threshold",
        description="Household income eligibility certification (< 2.5L)",
        category="Financial",
    ),
    "domicile.status": VerificationScopeDefinition(
        scope_code="domicile.status",
        display_name="State Permanent Domicile",
        description="State residency certificate attestation",
        category="Civic",
    ),
    "document.authenticity": VerificationScopeDefinition(
        scope_code="document.authenticity",
        display_name="SHA-256 Document Integrity Seal",
        description="Content-addressed cryptographic document fingerprint",
        category="Security",
    ),
}


@dataclass
class MockInstitutionService:
    """A specific public service hosted by a sandbox institution."""

    id: str
    institution_code: str
    service_code: str
    service_name: str
    purpose: str
    allowed_scopes: list[str]
    status: str = "ACTIVE"
    environment: str = "SANDBOX"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "institution_code": self.institution_code,
            "service_code": self.service_code,
            "service_name": self.service_name,
            "purpose": self.purpose,
            "allowed_scopes": self.allowed_scopes,
            "status": self.status,
            "environment": self.environment,
            "created_at": self.created_at,
        }


@dataclass
class MockInstitutionEntity:
    """A relying sandbox institution hosting one or more services."""

    id: str
    institution_code: str
    name: str
    display_name: str
    category: str
    description: str
    services: list[MockInstitutionService]
    status: str = "ACTIVE"
    environment: str = "SANDBOX"
    contact_name: str = "Sandbox Admin"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "institution_code": self.institution_code,
            "name": self.name,
            "display_name": self.display_name,
            "category": self.category,
            "description": self.description,
            "services": [s.to_dict() for s in self.services],
            # Aggregate allowed scopes across all services
            "allowed_scopes": sorted(list({scope for s in self.services for scope in s.allowed_scopes})),
            "status": self.status,
            "environment": self.environment,
            "contact_name": self.contact_name,
            "created_at": self.created_at,
        }


def _build_default_template_institutions() -> list[MockInstitutionEntity]:
    return [
        MockInstitutionEntity(
            id="inst_edu_001",
            institution_code="EDU-DEMO-001",
            name="Education Department Demo",
            display_name="Education Scholarship Service (🧪 Hackathon Demo)",
            category="Education",
            description="Simulated higher education department verifying academic merit, family income, and state domicile.",
            services=[
                MockInstitutionService(
                    id="srv_edu_sch_01",
                    institution_code="EDU-DEMO-001",
                    service_code="EDU-SCHOLARSHIP-DEMO",
                    service_name="National Merit Scholarship Eligibility",
                    purpose="Merit-cum-Means Scholarship Eligibility Verification",
                    allowed_scopes=["education.qualification", "income.status", "domicile.status", "education_qualification", "income_status", "domicile_status"],
                )
            ],
        ),
        MockInstitutionEntity(
            id="inst_rev_001",
            institution_code="REV-DEMO-001",
            name="Revenue Department Demo",
            display_name="Revenue Certificate Service (🧪 Hackathon Demo)",
            category="Revenue & Social Welfare",
            description="Simulated state revenue portal processing income attestation, community certificates, and domicile.",
            services=[
                MockInstitutionService(
                    id="srv_rev_cert_01",
                    institution_code="REV-DEMO-001",
                    service_code="REV-CERTIFICATE-DEMO",
                    service_name="EWS & Domicile Certificate Service",
                    purpose="EWS Scheme and State Domicile Attestation",
                    allowed_scopes=["identity.basic", "identity.address", "domicile.status", "identity_assertion", "income_status", "domicile_status"],
                )
            ],
        ),
        MockInstitutionEntity(
            id="inst_cit_001",
            institution_code="CIT-DEMO-001",
            name="Citizen Services Demo",
            display_name="Citizen Services Portal (🧪 Hackathon Demo)",
            category="Local Administration",
            description="Simulated municipal administration portal verifying resident identity and address proof.",
            services=[
                MockInstitutionService(
                    id="srv_cit_portal_01",
                    institution_code="CIT-DEMO-001",
                    service_code="CIT-PORTAL-DEMO",
                    service_name="Municipal Resident Registration",
                    purpose="Municipal Resident Title & Address Verification",
                    allowed_scopes=["identity.basic", "identity.address", "identity_assertion", "domicile_status"],
                )
            ],
        ),
    ]


class MockInstitutionRegistry:
    """Production-Style Institutional Integration Framework for DigiIn."""

    def __init__(self):
        self._institutions: dict[str, MockInstitutionEntity] = {}
        self._applications: dict[str, dict[str, Any]] = {}
        self.reset_hackathon_demo()

    def list_institutions(self) -> list[dict[str, Any]]:
        return [inst.to_dict() for inst in self._institutions.values()]

    def list_scopes(self) -> list[dict[str, Any]]:
        return [
            {
                "scope_code": s.scope_code,
                "display_name": s.display_name,
                "description": s.description,
                "category": s.category,
            }
            for s in STANDARDIZED_SCOPES.values()
        ]

    def get_institution(self, institution_code: str) -> MockInstitutionEntity | None:
        # Support both new codes (REV-DEMO-001, CIT-DEMO-001) and legacy aliases (REV-DEMO-002, ADM-DEMO-003)
        code = institution_code.upper()
        if code in self._institutions:
            return self._institutions[code]
        if code == "REV-DEMO-002" and "REV-DEMO-001" in self._institutions:
            return self._institutions["REV-DEMO-001"]
        if code == "ADM-DEMO-003" and "CIT-DEMO-001" in self._institutions:
            return self._institutions["CIT-DEMO-001"]
        return None

    def get_service(self, service_code: str) -> MockInstitutionService | None:
        code = service_code.upper()
        for inst in self._institutions.values():
            for srv in inst.services:
                if srv.service_code == code:
                    return srv
        return None

    def validate_service_scope(
        self, institution_code: str, requested_scopes: list[str], service_code: str | None = None
    ) -> tuple[bool, list[str]]:
        """Checks if requested scopes exceed the institution or service's accredited scope."""
        inst = self.get_institution(institution_code)
        if not inst:
            return False, requested_scopes

        allowed = set(inst.to_dict()["allowed_scopes"])
        if service_code:
            srv = self.get_service(service_code)
            if srv:
                allowed = set(srv.allowed_scopes)

        unauthorized = [s for s in requested_scopes if s not in allowed]
        return len(unauthorized) == 0, unauthorized

    def create_verification_request(
        self,
        institution_code: str,
        account_id: str,
        purpose: str,
        requested_scopes: list[str],
        service_code: str | None = None,
        ttl_seconds: int = 900,  # 15 minutes
    ) -> dict[str, Any]:
        """Creates a verification transaction through DigiIn Verification Layer."""
        inst = self.get_institution(institution_code)
        if not inst:
            raise KeyError(f"Sandbox institution '{institution_code}' not found.")

        # 1. Scope accreditation check
        is_valid_scope, unauthorized = self.validate_service_scope(
            institution_code, requested_scopes, service_code
        )
        if not is_valid_scope:
            raise PermissionError(
                f"UNAUTHORIZED_SCOPE: Institution '{inst.name}' is not accredited for requested scopes: {unauthorized}"
            )

        # 2. Delegate to DigiIn Verification Gateway
        req = verification_layer.create_request(
            digiin_account_id=account_id,
            requesting_service_id=inst.institution_code,
            service_name=inst.display_name,
            purpose=purpose,
            requested_attributes=requested_scopes,
            ttl_seconds=ttl_seconds,
        )

        app_id = f"APP-{inst.institution_code}-{uuid4().hex[:6].upper()}"
        app_record = {
            "application_id": app_id,
            "institution_code": inst.institution_code,
            "service_code": service_code or (inst.services[0].service_code if inst.services else "DEFAULT"),
            "institution_name": inst.name,
            "account_id": account_id,
            "purpose": purpose,
            "requested_scopes": requested_scopes,
            "status": "AWAITING_CONSENT",
            "request_reference": req["request_reference"],
            "created_at": datetime.now(UTC).isoformat(),
            "results": None,
        }
        self._applications[app_id] = app_record
        return {"application": app_record, "verification_request": req}

    def list_applications(self, institution_code: str | None = None) -> list[dict[str, Any]]:
        apps = list(self._applications.values())
        if institution_code:
            code = institution_code.upper()
            apps = [a for a in apps if a["institution_code"].upper() == code]
        return sorted(apps, key=lambda x: x["created_at"], reverse=True)

    def reset_hackathon_demo(self) -> dict[str, Any]:
        """Restores the complete hackathon demo environment to a deterministic baseline state."""
        template_institutions = _build_default_template_institutions()
        self._institutions = {inst.institution_code: inst for inst in template_institutions}
        self._applications.clear()

        # Seed initial pending applications
        self._applications["APP-EDU-901"] = {
            "application_id": "APP-EDU-901",
            "institution_code": "EDU-DEMO-001",
            "service_code": "EDU-SCHOLARSHIP-DEMO",
            "institution_name": "Education Department Demo",
            "account_id": "DI-7K4M-9Q2X-8P6R",
            "purpose": "Merit Scholarship 2026",
            "requested_scopes": ["education.qualification", "income.status", "domicile.status"],
            "status": "AWAITING_VERIFICATION",
            "request_reference": "VR-82J4K7",
            "created_at": datetime.now(UTC).isoformat(),
            "results": None,
        }

        return {
            "status": "success",
            "message": "Hackathon demo environment successfully reset to production-style template baseline.",
            "demo_citizen": {
                "account_id": "DI-7K4M-9Q2X-8P6R",
                "name": "Rahul Sharma (Demo Citizen)",
                "status": "Active & Verified",
            },
            "sandbox_institutions_count": len(self._institutions),
            "total_services_count": sum(len(i.services) for i in self._institutions.values()),
            "timestamp": datetime.now(UTC).isoformat(),
        }


# Global Template-Based Sandbox Registry Singleton
mock_institution_registry = MockInstitutionRegistry()
