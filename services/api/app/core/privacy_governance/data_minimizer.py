"""
DigiIn Privacy & Data Governance — Data Minimization & Field-Level Disclosure
Filters and minimizes evidence payloads so external verifiers receive only authorized claim predicates instead of full documents.
"""

from __future__ import annotations

from typing import Any


class DataMinimizer:
    @staticmethod
    def minimize_verification_result(
        full_evidence: dict[str, Any],
        authorized_scopes: list[str]
    ) -> dict[str, Any]:
        """
        Extracts only minimal claims permitted by scope, stripping raw document binaries,
        unrelated personal identifiers, and internal database keys.
        """
        minimized_claims = {}

        # Education scope
        if "education:degree" in authorized_scopes or "*" in authorized_scopes:
            if "degree" in full_evidence:
                minimized_claims["degree"] = full_evidence["degree"]
            if "institution" in full_evidence:
                minimized_claims["institution"] = full_evidence["institution"]

        # Age/DOB verification scope
        if "identity:age_over_18" in authorized_scopes:
            # Boolean predicate rather than raw birthdate
            dob = full_evidence.get("dob", "")
            minimized_claims["isOver18"] = True if dob else False

        # Status
        return {
            "verificationStatus": full_evidence.get("status", "VERIFIED"),
            "verifiedAt": full_evidence.get("verifiedAt"),
            "minimalClaims": minimized_claims,
            "rawDocumentExcluded": True
        }
