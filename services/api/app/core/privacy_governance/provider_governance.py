"""
DigiIn Privacy & Data Governance — Provider Data Governance & Contract Enforcement
Enforces minimization boundaries and data protection rules on external provider egress/ingress.
"""

from __future__ import annotations

from typing import Any


class ProviderDataGovernance:
    @staticmethod
    def sanitize_provider_egress(
        subject_id: str,
        document_type: str,
        provider_id: str
    ) -> dict[str, Any]:
        """Ensures DigiIn transmits only opaque identifiers and required verification parameters to providers."""
        return {
            "subjectReference": subject_id,
            "documentType": document_type,
            "providerId": provider_id,
            "fullProfileExcluded": True,
            "crossAccountLinkageExcluded": True
        }

    @staticmethod
    def filter_provider_ingress(
        raw_provider_response: dict[str, Any],
        required_claims: list[str]
    ) -> dict[str, Any]:
        """Strips extraneous unrequested provider fields before storing verified claims in DigiIn."""
        filtered = {"status": raw_provider_response.get("status", "VERIFIED")}
        for claim in required_claims:
            if claim in raw_provider_response:
                filtered[claim] = raw_provider_response[claim]
        return filtered
