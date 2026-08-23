"""
DigiIn Trust Network Expansion — Zero-PII Claim Discovery Catalog
Enables verifiers to discover available trust claim types across domains without exposing subject or citizen information.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CatalogEntry:
    domain: str  # "EDUCATION" | "IDENTITY" | "EMPLOYMENT" | "LICENSING" | "HEALTHCARE"
    claim_type: str
    description: str
    required_assurance: str
    accredited_issuers_count: int

class ClaimCatalog:
    def __init__(self):
        self._entries: list[CatalogEntry] = []
        self._seed_default_catalog()

    def _seed_default_catalog(self):
        self._entries.extend([
            CatalogEntry(
                domain="EDUCATION",
                claim_type="education.degree",
                description="Higher education bachelor/master degree completion",
                required_assurance="A3_HIGH_ASSURANCE",
                accredited_issuers_count=45
            ),
            CatalogEntry(
                domain="IDENTITY",
                claim_type="identity.age_over_18",
                description="Zero-knowledge adult qualification claim",
                required_assurance="A4_REGULATED",
                accredited_issuers_count=12
            ),
            CatalogEntry(
                domain="LICENSING",
                claim_type="licence.driving",
                description="Motor vehicle driving authorization and category",
                required_assurance="A4_REGULATED",
                accredited_issuers_count=28
            ),
            CatalogEntry(
                domain="EMPLOYMENT",
                claim_type="employment.tenure",
                description="Verified enterprise employment and job title tenure",
                required_assurance="A2_VERIFIED_ORG",
                accredited_issuers_count=150
            ),
        ])

    def list_catalog(self, domain_filter: str | None = None) -> list[dict[str, Any]]:
        results = self._entries
        if domain_filter:
            results = [e for e in results if e.domain.upper() == domain_filter.upper()]

        return [
            {
                "domain": e.domain,
                "claimType": e.claim_type,
                "description": e.description,
                "requiredAssurance": e.required_assurance,
                "accreditedIssuersCount": e.accredited_issuers_count
            }
            for e in results
        ]
