"""
DigiIn Long-Term Infrastructure — DigiIn Platform SDK & Standard Error Model
Provides a standardized client SDK and universal error codes for institutional developers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class PlatformErrorCode:
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    CONSENT_REQUIRED = "CONSENT_REQUIRED"
    CONSENT_DENIED = "CONSENT_DENIED"
    CLAIM_NOT_FOUND = "CLAIM_NOT_FOUND"
    CLAIM_EXPIRED = "CLAIM_EXPIRED"
    CLAIM_REVOKED = "CLAIM_REVOKED"
    ISSUER_NOT_TRUSTED = "ISSUER_NOT_TRUSTED"
    VERIFIER_NOT_AUTHORIZED = "VERIFIER_NOT_AUTHORIZED"
    POLICY_DENIED = "POLICY_DENIED"
    PROOF_INVALID = "PROOF_INVALID"
    PROOF_EXPIRED = "PROOF_EXPIRED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"

@dataclass
class SDKVerificationResponse:
    status: str  # "VERIFIED" | "REJECTED" | "ERROR"
    assurance_level: str
    claims: dict[str, Any]
    error_code: str | None = None
    error_message: str | None = None

class DigiInPlatformSDK:
    def __init__(self, trust_registry: Any, consent_mgr: Any, proof_engine: Any):
        self.trust_registry = trust_registry
        self.consent_mgr = consent_mgr
        self.proof_engine = proof_engine

    def verify(
        self,
        proof: Any,
        expected_verifier_id: str,
        expected_purpose: str,
        credential_id: str
    ) -> SDKVerificationResponse:
        # 1. Verify consent
        if not self.consent_mgr.validate_consent(proof.subject_id, expected_verifier_id, expected_purpose, credential_id):
            return SDKVerificationResponse(
                status="REJECTED",
                assurance_level="NONE",
                claims={},
                error_code=PlatformErrorCode.CONSENT_DENIED,
                error_message="Citizen consent is missing, expired, or revoked."
            )

        # 2. Verify proof status
        if proof.status != "VALID":
            return SDKVerificationResponse(
                status="REJECTED",
                assurance_level="NONE",
                claims={},
                error_code=PlatformErrorCode.PROOF_INVALID,
                error_message="Proof or underlying credential is not valid."
            )

        return SDKVerificationResponse(
            status="VERIFIED",
            assurance_level="A3_HIGH_ASSURANCE",
            claims=proof.disclosed_data
        )
