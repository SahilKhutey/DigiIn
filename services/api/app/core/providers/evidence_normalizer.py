"""
DigiIn Provider Integration Subsystem — Evidence Normalization & Provenance
Converts provider-specific response payloads into canonical ProviderEvidence objects with strict provenance tracking.
"""

from __future__ import annotations

import time
from typing import Any


class ProviderEvidence:
    def __init__(
        self,
        provider_id: str,
        subject_reference: str,
        claim_type: str,
        value: Any,
        status: str = "VERIFIED",  # "VERIFIED" | "NOT_FOUND" | "INVALID" | "UNAVAILABLE"
        source_reference: str = "",
        assurance_level: str = "HIGH",
        request_id: str = "",
        retrieved_at: float | None = None
    ):
        self.provider_id = provider_id
        self.subject_reference = subject_reference
        self.claim_type = claim_type
        self.value = value
        self.status = status
        self.source_reference = source_reference
        self.assurance_level = assurance_level
        self.request_id = request_id
        self.retrieved_at = retrieved_at or time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "providerId": self.provider_id,
            "subjectReference": self.subject_reference,
            "claimType": self.claim_type,
            "value": self.value,
            "status": self.status,
            "sourceReference": self.source_reference,
            "assuranceLevel": self.assurance_level,
            "requestId": self.request_id,
            "retrievedAt": self.retrieved_at,
        }

class EvidenceNormalizer:
    @staticmethod
    def normalize(
        provider_id: str,
        raw_response: dict[str, Any],
        claim_type: str,
        subject_ref: str,
        request_id: str
    ) -> ProviderEvidence:
        """
        Normalize heterogeneous provider data into canonical DigiIn claim facts.
        """
        # 1. CBSE Board Normalization
        if "provider_cbse" in provider_id:
            val = {
                "qualification": raw_response.get("qualification_title", "Class XII Examination"),
                "percentage": raw_response.get("total_percentage", 0.0),
                "passing_year": raw_response.get("exam_year", 2024),
                "result": raw_response.get("result_status", "PASSED"),
            }
            return ProviderEvidence(
                provider_id=provider_id,
                subject_reference=subject_ref,
                claim_type="EDUCATION",
                value=val,
                status="VERIFIED" if raw_response.get("result_status") == "PASSED" else "NOT_FOUND",
                source_reference=f"CBSE-ROLL-{raw_response.get('roll_no', 'NA')}",
                assurance_level="HIGH",
                request_id=request_id
            )

        # 2. University of Delhi Normalization
        if "provider_delhi_univ" in provider_id or "university" in provider_id:
            val = {
                "degree": raw_response.get("degree_program", "Bachelor's Degree"),
                "cgpa": raw_response.get("cgpa", 0.0),
                "division": raw_response.get("division", "FIRST_CLASS"),
                "completed": raw_response.get("degree_verified", True),
            }
            return ProviderEvidence(
                provider_id=provider_id,
                subject_reference=subject_ref,
                claim_type="EDUCATION",
                value=val,
                status="VERIFIED" if raw_response.get("degree_verified") else "NOT_FOUND",
                source_reference=f"DU-ENROLL-{raw_response.get('enrollment_no', 'NA')}",
                assurance_level="HIGH",
                request_id=request_id
            )

        # 3. Transport Ministry Driving Licence Normalization
        if "sarathi" in provider_id or "parivahan" in provider_id:
            val = {
                "licence_number": raw_response.get("licence_number"),
                "vehicle_classes": raw_response.get("vehicle_classes", []),
                "valid_until": raw_response.get("valid_until"),
                "age_18_plus": raw_response.get("age_eligible_18_plus", True),
            }
            return ProviderEvidence(
                provider_id=provider_id,
                subject_reference=subject_ref,
                claim_type=claim_type,
                value=val,
                status="VERIFIED" if raw_response.get("status") == "ACTIVE_VALID" else "INVALID",
                source_reference=f"MORTH-DL-{raw_response.get('licence_number', 'NA')}",
                assurance_level="HIGH",
                request_id=request_id
            )

        # Generic / Sandbox fallback normalization
        return ProviderEvidence(
            provider_id=provider_id,
            subject_reference=subject_ref,
            claim_type=claim_type,
            value=raw_response,
            status="VERIFIED" if raw_response.get("verified", True) else "NOT_FOUND",
            source_reference=f"GENERIC-REF-{provider_id}",
            assurance_level="MEDIUM",
            request_id=request_id
        )
