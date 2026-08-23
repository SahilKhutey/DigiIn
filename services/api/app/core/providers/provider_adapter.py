"""
DigiIn Provider Integration Subsystem — Provider Adapter Framework
Defines the ProviderAdapter interface and concrete adapters for Government, University, Board, and Sandbox environments.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ProviderVerificationRequest:
    def __init__(
        self,
        request_id: str,
        subject_reference: str,
        claim_types: list[str],
        purpose: str,
        correlation_id: str,
        parameters: dict[str, Any] | None = None
    ):
        self.request_id = request_id
        self.subject_reference = subject_reference
        self.claim_types = claim_types
        self.purpose = purpose
        self.correlation_id = correlation_id
        self.parameters = parameters or {}

class RawProviderResponse:
    def __init__(
        self,
        provider_id: str,
        status_code: int,
        raw_body: dict[str, Any],
        signature: str | None = None,
        latency_ms: float = 50.0
    ):
        self.provider_id = provider_id
        self.status_code = status_code
        self.raw_body = raw_body
        self.signature = signature
        self.latency_ms = latency_ms

class ProviderAdapter(ABC):
    @abstractmethod
    def verify(self, request: ProviderVerificationRequest) -> RawProviderResponse:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass

class BoardAdapter(ProviderAdapter):
    """Adapter for Secondary / Higher Secondary Examination Boards (e.g. CBSE)."""
    def __init__(self, provider_id: str = "provider_cbse_in"):
        self.provider_id = provider_id

    def verify(self, request: ProviderVerificationRequest) -> RawProviderResponse:
        # Simulates CBSE Board authoritative database response
        roll_number = request.parameters.get("roll_number", "CBSE-2024-88421")
        year = request.parameters.get("passing_year", 2024)

        raw_data = {
            "board": "Central Board of Secondary Education",
            "candidate_ref": request.subject_reference,
            "roll_no": roll_number,
            "exam_year": year,
            "stream": "Science",
            "result_status": "PASSED",
            "total_percentage": 88.5,
            "qualification_title": "Senior School Certificate Examination (Class XII)",
            "issued_on": "2024-05-13T10:00:00Z"
        }
        return RawProviderResponse(
            provider_id=self.provider_id,
            status_code=200,
            raw_body=raw_data,
            signature="sig_cbse_ed25519_authoritative_cert"
        )

    def health_check(self) -> bool:
        return True

class UniversityAdapter(ProviderAdapter):
    """Adapter for Universities and Higher Education Institutions."""
    def __init__(self, provider_id: str = "provider_delhi_univ"):
        self.provider_id = provider_id

    def verify(self, request: ProviderVerificationRequest) -> RawProviderResponse:
        raw_data = {
            "university": "University of Delhi",
            "student_id": request.subject_reference,
            "enrollment_no": "DU-2021-9941",
            "degree_program": "Bachelor of Technology in Computer Science",
            "cgpa": 8.92,
            "division": "FIRST_CLASS_DISTINCTION",
            "convocation_date": "2025-02-28",
            "degree_verified": True
        }
        return RawProviderResponse(
            provider_id=self.provider_id,
            status_code=200,
            raw_body=raw_data,
            signature="sig_du_ed25519_cert"
        )

    def health_check(self) -> bool:
        return True

class GovernmentAdapter(ProviderAdapter):
    """Adapter for State/Central Government Registries (e.g. Parivahan Driving Licences)."""
    def __init__(self, provider_id: str = "provider_sarathi_parivahan"):
        self.provider_id = provider_id

    def verify(self, request: ProviderVerificationRequest) -> RawProviderResponse:
        raw_data = {
            "authority": "Ministry of Road Transport and Highways",
            "licence_number": "DL-0420210088912",
            "holder_ref": request.subject_reference,
            "vehicle_classes": ["MCWG", "LMV"],
            "valid_until": "2041-08-15",
            "status": "ACTIVE_VALID",
            "age_eligible_18_plus": True
        }
        return RawProviderResponse(
            provider_id=self.provider_id,
            status_code=200,
            raw_body=raw_data,
            signature="sig_morth_ed25519_cert"
        )

    def health_check(self) -> bool:
        return True

class SandboxSimulatorAdapter(ProviderAdapter):
    """Deterministic Simulator for testing all integration failure states."""
    def __init__(self, provider_id: str = "provider_sandbox_sim"):
        self.provider_id = provider_id
        self.simulated_mode = "SUCCESS"  # "SUCCESS" | "NOT_FOUND" | "TIMEOUT" | "CONFLICT" | "ERROR"

    def set_mode(self, mode: str):
        self.simulated_mode = mode

    def verify(self, request: ProviderVerificationRequest) -> RawProviderResponse:
        if self.simulated_mode == "TIMEOUT":
            raise TimeoutError("Simulated provider upstream timeout (10000ms exceeded).")
        if self.simulated_mode == "ERROR":
            raise RuntimeError("Simulated provider upstream internal server error 500.")
        if self.simulated_mode == "NOT_FOUND":
            return RawProviderResponse(
                provider_id=self.provider_id,
                status_code=404,
                raw_body={"error": "RECORD_NOT_FOUND", "message": "No matching subject record located."}
            )
        if self.simulated_mode == "CONFLICT":
            return RawProviderResponse(
                provider_id=self.provider_id,
                status_code=200,
                raw_body={"claimType": "EDUCATION", "degree": "B.Sc (Conflicting Degree)"}
            )

        # Default Success
        return RawProviderResponse(
            provider_id=self.provider_id,
            status_code=200,
            raw_body={"claimType": "EDUCATION", "qualification": "B.Tech", "verified": True}
        )

    def health_check(self) -> bool:
        return self.simulated_mode != "ERROR"
