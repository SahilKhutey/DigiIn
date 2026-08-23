"""
DigiIn Web Surfaces — Public Directory & Trust Surfaces Layer
Provides public service catalog (/services), accredited organization directory (/organizations),
how-it-works workflow steps, and security trust policies.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PublicServiceItem:
    id: str
    name: str
    organization_name: str
    category: str  # "Education", "Government", "Employment", "Licensing", "Financial"
    purpose: str
    requested_claims: list[str]
    description: str
    verified: bool = True

@dataclass
class PublicOrganizationItem:
    id: str
    name: str
    type: str  # "UNIVERSITY", "GOVERNMENT", "EMPLOYER", "FINANCIAL"
    verified: bool
    service_count: int
    accreditation_level: str  # "A3_HIGH_ASSURANCE", "A2_STATUTORY"

class PublicDirectoryManager:
    def __init__(self):
        self._services: list[PublicServiceItem] = []
        self._organizations: list[PublicOrganizationItem] = []
        self._seed_directory()

    def _seed_directory(self):
        self._services = [
            PublicServiceItem(
                id="srv_scholarship_portal",
                name="National Scholarship Verification",
                organization_name="Ministry of Education",
                category="Scholarships",
                purpose="SCHOLARSHIP_ELIGIBILITY",
                requested_claims=["education.degree", "education.graduationYear"],
                description="Authoritative verification of degree qualifications for central scholarships"
            ),
            PublicServiceItem(
                id="srv_du_admissions",
                name="Undergraduate Admissions Verification",
                organization_name="University of Delhi",
                category="Education",
                purpose="ADMISSION_VERIFICATION",
                requested_claims=["education.class_xii_marksheet", "identity.name"],
                description="Instant verification of Class XII marks for Delhi University admissions"
            ),
            PublicServiceItem(
                id="srv_sarathi_transport",
                name="Driving Licence Verification",
                organization_name="Sarathi Transport Department",
                category="Licensing",
                purpose="LICENCE_VERIFICATION",
                requested_claims=["licence.number", "licence.validity"],
                description="Digital validation of driving licence credentials for public transport"
            )
        ]

        self._organizations = [
            PublicOrganizationItem(
                id="org_ministry_edu",
                name="Ministry of Education",
                type="GOVERNMENT",
                verified=True,
                service_count=4,
                accreditation_level="A3_HIGH_ASSURANCE"
            ),
            PublicOrganizationItem(
                id="org_delhi_university",
                name="University of Delhi",
                type="UNIVERSITY",
                verified=True,
                service_count=2,
                accreditation_level="A3_HIGH_ASSURANCE"
            ),
            PublicOrganizationItem(
                id="org_delhi_transport",
                name="Sarathi Transport Department",
                type="GOVERNMENT",
                verified=True,
                service_count=3,
                accreditation_level="A2_STATUTORY"
            )
        ]

    def get_public_services(self, category_filter: str | None = None, search: str | None = None) -> list[PublicServiceItem]:
        res = self._services
        if category_filter:
            res = [s for s in res if s.category.lower() == category_filter.lower()]
        if search:
            q = search.lower()
            res = [s for s in res if q in s.name.lower() or q in s.organization_name.lower() or q in s.description.lower()]
        return res

    def get_public_organizations(self, type_filter: str | None = None, search: str | None = None) -> list[PublicOrganizationItem]:
        res = self._organizations
        if type_filter:
            res = [o for o in res if o.type.lower() == type_filter.lower()]
        if search:
            q = search.lower()
            res = [o for o in res if q in o.name.lower()]
        return res

    @staticmethod
    def get_how_it_works_steps() -> list[dict[str, str]]:
        return [
            {"step": "1", "title": "Create DigiIn Account", "desc": "Sign up with your identity to obtain a secure DigiIn Account ID."},
            {"step": "2", "title": "Add / Receive Credentials", "desc": "Acquire verified credentials directly from accredited institutions."},
            {"step": "3", "title": "Credentials Get Verified", "desc": "Cryptographic authenticity and issuer signatures are validated."},
            {"step": "4", "title": "Service Requests Verification", "desc": "An external service requests proof with a declared purpose."},
            {"step": "5", "title": "You Review & Approve", "desc": "Review exact requested claims and grant explicit consent."},
            {"step": "6", "title": "DigiIn Verifies", "desc": "DigiIn verifies the credential against trust registries."},
            {"step": "7", "title": "Service Receives Result", "desc": "The service receives verification with minimal claim disclosure."}
        ]
