"""
DigiIn Verification Hardening — Privacy & Minimal Disclosure Validator
Asserts that service responses contain exclusively the consented claims, without leaking unrequested attributes or raw document files.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PrivacyDisclosureAuditResult:
    is_compliant: bool
    disclosed_claims: list[str]
    forbidden_claims_detected: list[str]
    raw_files_leaked: bool
    summary: str

class PrivacyProofValidator:
    FORBIDDEN_UNREQUESTED_KEYS = {"rollNumber", "grade", "dob", "address", "phone", "aadhaar", "raw_file", "document_binary"}

    @staticmethod
    def audit_service_disclosure(
        requested_and_consented_claims: list[str],
        returned_payload: dict[str, Any]
    ) -> PrivacyDisclosureAuditResult:
        claims_in_payload = set(returned_payload.get("claims", {}).keys())
        consented_set = set(requested_and_consented_claims)

        # Check for unrequested leaks
        forbidden_leaks = [k for k in claims_in_payload if k not in consented_set]
        raw_leak = "raw_file" in returned_payload or "document_binary" in returned_payload

        compliant = len(forbidden_leaks) == 0 and not raw_leak
        summary = "Minimal disclosure perfectly preserved." if compliant else f"PRIVACY VIOLATION: Leaked unrequested fields {forbidden_leaks}"

        return PrivacyDisclosureAuditResult(
            is_compliant=compliant,
            disclosed_claims=list(claims_in_payload),
            forbidden_claims_detected=forbidden_leaks,
            raw_files_leaked=raw_leak,
            summary=summary
        )
