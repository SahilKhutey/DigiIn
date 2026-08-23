"""
DigiIn Institutional Scale — Service Directory & Integration Marketplace
Exposes public zero-PII service listings and pre-packaged integration templates for rapid institutional deployment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ServiceEntry:
    id: str
    name: str
    organization_name: str
    category: str  # "GOVERNMENT" | "EDUCATION" | "EMPLOYMENT" | "LICENSING" | "BENEFITS"
    supported_claims: list[str]
    verification_mode: str = "TRUST_NETWORK"
    status: str = "OPERATIONAL"

@dataclass
class IntegrationPackage:
    id: str
    name: str
    version: str
    claim_types: list[str]
    required_scopes: list[str]
    required_assurance: str
    api_version: str = "v1"
    status: str = "ACTIVE"

class ServiceDirectory:
    def __init__(self):
        self._services: list[ServiceEntry] = []
        self._seed_default_services()

    def _seed_default_services(self):
        self._services.extend([
            ServiceEntry(
                id="srv_national_scholarship",
                name="National Scholarship Portal Verification",
                organization_name="Ministry of Education",
                category="EDUCATION",
                supported_claims=["education.degree", "education.marksheet"]
            ),
            ServiceEntry(
                id="srv_delhi_transport",
                name="Sarathi Driving Licence Verification",
                organization_name="Transport Department",
                category="LICENSING",
                supported_claims=["licence.driving"]
            ),
        ])

    def list_services(self, category: str | None = None) -> list[dict[str, Any]]:
        entries = self._services
        if category:
            entries = [s for s in entries if s.category.upper() == category.upper()]
        return [
            {
                "id": s.id,
                "name": s.name,
                "organizationName": s.organization_name,
                "category": s.category,
                "supportedClaims": s.supported_claims,
                "status": s.status
            }
            for s in entries
        ]

class IntegrationMarketplace:
    def __init__(self):
        self._packages: list[IntegrationPackage] = []
        self._seed_default_packages()

    def _seed_default_packages(self):
        self._packages.extend([
            IntegrationPackage(
                id="pkg_higher_edu_v1",
                name="Higher Education Degree Verification Pack",
                version="1.0.0",
                claim_types=["education.degree", "education.transcript"],
                required_scopes=["claims:request", "claims:verify"],
                required_assurance="A3_HIGH_ASSURANCE"
            ),
            IntegrationPackage(
                id="pkg_employment_v1",
                name="Enterprise Employment Tenure Pack",
                version="1.0.0",
                claim_types=["employment.tenure"],
                required_scopes=["claims:request"],
                required_assurance="A2_VERIFIED_ORG"
            ),
        ])

    def list_packages(self) -> list[dict[str, Any]]:
        return [
            {
                "id": p.id,
                "name": p.name,
                "version": p.version,
                "claimTypes": p.claim_types,
                "requiredScopes": p.required_scopes,
                "requiredAssurance": p.required_assurance,
                "status": p.status
            }
            for p in self._packages
        ]
