"""Public Service Registry & Application State Machine.

Provides a service-first catalogue of Indian public digital services that citizens
can apply for using pre-verified DigiIn credentials.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ApplicationStatus(StrEnum):
    INITIATED = "INITIATED"
    CLAIMS_DISCOVERED = "CLAIMS_DISCOVERED"
    CONSENT_REVIEWED = "CONSENT_REVIEWED"
    PROOF_MINTED = "PROOF_MINTED"
    SUBMITTED = "SUBMITTED"
    INSTITUTION_VERIFIED = "INSTITUTION_VERIFIED"
    REJECTED = "REJECTED"


@dataclass
class PublicServiceDefinition:
    service_id: str
    name: str
    department: str
    category: str
    description: str
    estimated_time_digiin: str
    estimated_time_traditional: str
    required_credentials: list[str]
    required_predicates: list[str]
    purpose: str
    validity_hours: int = 24


@dataclass
class ServiceApplication:
    application_id: str
    service_id: str
    service_name: str
    citizen_account_id: str
    citizen_name: str
    status: ApplicationStatus
    created_at: float
    updated_at: float
    disclosed_claims: dict[str, Any] = field(default_factory=dict)
    withheld_claims: list[str] = field(default_factory=list)
    proof_id: str | None = None
    proof_token: str | None = None
    institution_verification_result: dict[str, Any] | None = None


# Pre-configured public services catalogue
SERVICES_CATALOGUE: dict[str, PublicServiceDefinition] = {
    "srv_scholarship_du": PublicServiceDefinition(
        service_id="srv_scholarship_du",
        name="National Merit-cum-Means Scholarship",
        department="University of Delhi & National Scholarship Portal",
        category="Education & Higher Studies",
        description="Merit scholarship for eligible undergraduate students based on Class XII marks and family income criteria.",
        estimated_time_digiin="2 minutes",
        estimated_time_traditional="45 minutes (with 4 PDF uploads)",
        required_credentials=["MARKSHEET_XII", "DOMICILE_CERTIFICATE", "INCOME_CERTIFICATE"],
        required_predicates=["identity.fullName", "domicile.state", "income.is_eligible", "education.passing_score"],
        purpose="Scholarship Eligibility & Academic Merit Determination",
        validity_hours=24,
    ),
    "srv_caste_certificate": PublicServiceDefinition(
        service_id="srv_caste_certificate",
        name="State Certificate Verification & Renewal",
        department="Department of Revenue & Land Records",
        category="Revenue & Social Welfare",
        description="Instant renewal and validation of caste and community credentials.",
        estimated_time_digiin="3 minutes",
        estimated_time_traditional="3 weeks",
        required_credentials=["IDENTITY_AADHAAR", "DOMICILE_CERTIFICATE"],
        required_predicates=["identity.fullName", "domicile.state"],
        purpose="Social Welfare Certificate Verification",
        validity_hours=48,
    ),
    "srv_university_admission": PublicServiceDefinition(
        service_id="srv_university_admission",
        name="Undergraduate Admissions Eligibility",
        department="Central Universities Entrance Authority",
        category="Higher Education",
        description="Verify Class X/XII eligibility and state quota for university admissions without submitting physical marksheet copies.",
        estimated_time_digiin="2 minutes",
        estimated_time_traditional="1 hour",
        required_credentials=["MARKSHEET_XII", "DOMICILE_CERTIFICATE"],
        required_predicates=["identity.fullName", "education.passing_score", "domicile.state"],
        purpose="University Admission Eligibility Verification",
        validity_hours=72,
    ),
}


class PublicServiceRegistry:
    """Manages public service definitions and live citizen application lifecycles."""

    def __init__(self) -> None:
        self._services: dict[str, PublicServiceDefinition] = dict(SERVICES_CATALOGUE)
        self._applications: dict[str, ServiceApplication] = {}

    def list_services(self) -> list[dict[str, Any]]:
        """Lists available public digital services with estimated times."""
        return [
            {
                "service_id": s.service_id,
                "name": s.name,
                "department": s.department,
                "category": s.category,
                "description": s.description,
                "estimated_time_digiin": s.estimated_time_digiin,
                "estimated_time_traditional": s.estimated_time_traditional,
                "required_credentials_count": len(s.required_credentials),
                "purpose": s.purpose,
            }
            for s in self._services.values()
        ]

    def get_service(self, service_id: str) -> PublicServiceDefinition:
        if service_id not in self._services:
            raise KeyError(f"Public service '{service_id}' not found.")
        return self._services[service_id]

    def start_application(
        self, service_id: str, citizen_account_id: str, citizen_name: str
    ) -> ServiceApplication:
        """Starts an instant public service application for the citizen."""
        service = self.get_service(service_id)
        app_id = f"APP-{service_id.upper()}-{uuid.uuid4().hex[:8].upper()}"
        now = time.time()

        app = ServiceApplication(
            application_id=app_id,
            service_id=service.service_id,
            service_name=service.name,
            citizen_account_id=citizen_account_id,
            citizen_name=citizen_name,
            status=ApplicationStatus.INITIATED,
            created_at=now,
            updated_at=now,
        )
        self._applications[app_id] = app
        return app

    def get_application(self, app_id: str) -> ServiceApplication:
        if app_id not in self._applications:
            raise KeyError(f"Application '{app_id}' not found.")
        return self._applications[app_id]

    def update_application(self, app: ServiceApplication) -> None:
        app.updated_at = time.time()
        self._applications[app.application_id] = app


# Singleton instance
service_registry = PublicServiceRegistry()
