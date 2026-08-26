"""Public Service & Flagship Scholarship Application API Router."""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.proofs import (
    KeyManager,
    ProofSigningService,
    TrustedIssuer,
    TrustRegistry,
    VerifiedClaim,
)
from app.core.public_service import (
    ApplicationStatus,
    data_saver_engine,
    service_registry,
    sharing_review_generator,
)

router = APIRouter(prefix="/public-service", tags=["Public Services & Scholarship Flow"])


# Pydantic Request/Response Models
class StartScholarshipRequest(BaseModel):
    citizen_account_id: str = Field(default="DGI-7K4M-X9P2-2026", description="Sovereign citizen account ID")
    citizen_name: str = Field(default="Rahul Sharma", description="Applicant full name")


class ConsentAndSubmitRequest(BaseModel):
    citizen_account_id: str = Field(default="DGI-7K4M-X9P2-2026")
    consent_granted: bool = Field(default=True, description="Explicit purpose-bound citizen consent")


@router.get("/services")
def list_public_services() -> dict[str, Any]:
    """Lists available public digital services with estimated times (DigiIn vs Traditional)."""
    services = service_registry.list_services()
    return {
        "status": "success",
        "count": len(services),
        "services": services,
        "data_saver_active": data_saver_engine.is_enabled(),
    }


@router.post("/scholarship/apply")
def start_scholarship_application(request: StartScholarshipRequest) -> dict[str, Any]:
    """Initiates an instant scholarship application for the citizen using pre-verified DigiIn claims."""
    app = service_registry.start_application(
        service_id="srv_scholarship_du",
        citizen_account_id=request.citizen_account_id,
        citizen_name=request.citizen_name,
    )
    app.status = ApplicationStatus.CLAIMS_DISCOVERED
    service_registry.update_application(app)

    return {
        "status": "success",
        "application_id": app.application_id,
        "service_name": app.service_name,
        "citizen_name": app.citizen_name,
        "application_status": app.status.value,
        "next_step": f"/api/v1/public-service/scholarship/{app.application_id}/sharing-review",
        "estimated_time": "2 minutes with DigiIn",
    }


@router.get("/scholarship/{app_id}/sharing-review")
def get_sharing_review(app_id: str) -> dict[str, Any]:
    """Returns the signature Sharing Review screen: explicit shared predicates vs withheld private data."""
    try:
        review_data = sharing_review_generator.generate_review(app_id)
        raw_dict = {
            "application_id": review_data.application_id,
            "service_name": review_data.service_name,
            "requesting_institution": review_data.requesting_institution,
            "purpose": review_data.purpose,
            "validity_window": review_data.validity_window,
            "estimated_time_saved": review_data.estimated_time_saved,
            "privacy_badge": review_data.privacy_badge,
            "raw_files_transferred_bytes": review_data.raw_files_transferred_bytes,
            "shared_claims": [
                {
                    "field": c.field,
                    "label": c.label,
                    "value": c.value,
                    "is_shared": c.is_shared,
                    "reason": c.reason,
                }
                for c in review_data.shared_claims
            ],
            "withheld_claims": [
                {
                    "field": c.field,
                    "label": c.label,
                    "value": c.value,
                    "is_shared": c.is_shared,
                    "reason": c.reason,
                }
                for c in review_data.withheld_claims
            ],
        }

        # Apply Data Saver optimization if active
        optimized = data_saver_engine.optimize_payload(raw_dict)
        savings = data_saver_engine.calculate_savings(raw_dict, optimized)

        return {
            "status": "success",
            "review": optimized,
            "data_saver": {
                "active": savings.mode_active,
                "bytes_saved": savings.bytes_saved,
                "message": savings.message,
            },
        }
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/scholarship/{app_id}/consent-and-submit")
def consent_and_submit_scholarship(app_id: str, request: ConsentAndSubmitRequest) -> dict[str, Any]:
    """Citizen grants purpose-bound consent; DigiIn mints an Ed25519 cryptographic proof and submits the application."""
    if not request.consent_granted:
        raise HTTPException(status_code=400, detail="Explicit citizen consent is required to proceed.")

    try:
        app = service_registry.get_application(app_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Cryptographic proof setup
    key_manager = KeyManager()
    key_manager.generate_and_register_key("KEY-PUBLIC-SERVICE-ROOT")
    trust_registry = TrustRegistry()
    trust_registry.register_issuer(
        TrustedIssuer(
            id="iss_digiin_scholarship_authority",
            name="DigiIn Public Service Verification Authority",
            issuer_identifier="did:digiin:authority:root",
            trusted_proof_types=["SCHOLARSHIP_ELIGIBILITY_VERIFIED"],
            status="ACTIVE",
        )
    )
    signer = ProofSigningService(key_manager)

    disclosed_predicates = {
        "fullName": app.citizen_name,
        "domicile": "Chhattisgarh",
        "income_eligible": True,
        "academic_score_bracket": ">= 90% (94.2% Passed)",
    }

    claims = [
        VerifiedClaim(type="SCHOLARSHIP_ELIGIBILITY_VERIFIED", value=disclosed_predicates),
    ]

    proof = signer.mint_signed_proof(
        subject_id=app.citizen_account_id,
        claims=claims,
        purpose="Scholarship Eligibility & Academic Merit Determination",
        proof_type="SCHOLARSHIP_ELIGIBILITY_VERIFIED",
    )

    app.status = ApplicationStatus.SUBMITTED
    app.proof_id = proof["proofId"]
    app.disclosed_claims = disclosed_predicates
    app.withheld_claims = ["Aadhaar Number", "Raw Tax PDFs", "Raw Marksheet Scans", "Full Address"]
    app.institution_verification_result = {
        "verified": True,
        "signature_valid": True,
        "issuer_trusted": True,
        "verified_at": time.time(),
        "institution_verdict": "VERIFIED_ELIGIBLE",
    }
    service_registry.update_application(app)

    return {
        "status": "success",
        "application_id": app.application_id,
        "application_status": app.status.value,
        "proof_id": app.proof_id,
        "digest": proof.get("digest"),
        "raw_files_transferred": "0 Bytes",
        "message": "Scholarship application submitted in 2 minutes! Proof sent to University of Delhi.",
    }


@router.get("/institution/applications/{app_id}")
def get_institution_application_view(app_id: str) -> dict[str, Any]:
    """Institutional review view: University sees verified claims and mathematical proof without raw PDF binaries."""
    try:
        app = service_registry.get_application(app_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if app.status != ApplicationStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="Application has not yet been submitted by citizen.")

    return {
        "status": "success",
        "application_id": app.application_id,
        "service_name": app.service_name,
        "applicant_name": app.citizen_name,
        "verification_summary": {
            "identity": "✓ Verified (DigiIn Sovereign Trust)",
            "domicile": "✓ Chhattisgarh Resident (Verified)",
            "income": "✓ Eligible (< 2.5L Threshold)",
            "education": "✓ CBSE Class XII (94.2% Marks)",
        },
        "cryptographic_evidence": {
            "proof_id": app.proof_id,
            "signature_status": "Valid Ed25519 (RFC 8785 Canonicalized)",
            "issuer_trust": "DigiIn Public Service Verification Authority (Trusted)",
            "raw_files_held": "0 Bytes (Zero Storage Liability)",
        },
        "institution_action": "READY_FOR_ADMISSION_APPROVAL",
    }


@router.get("/data-saver/status")
def get_data_saver_status() -> dict[str, Any]:
    """Returns Data Saver mode active status and network optimization details."""
    return {
        "data_saver_active": data_saver_engine.is_enabled(),
        "optimizations": [
            "Zero heavy PDF binary transfers",
            "Compressed JSON payload envelopes (>= 60% byte reduction)",
            "Lightweight CSS skeleton loading",
            "Retry-safe idempotent offline requests",
        ],
        "message": "Data Saver is on. DigiIn will use less data.",
    }


@router.post("/demo/reset")
def reset_demo_scenario() -> dict[str, Any]:
    """1-Click instant reset of the deterministic sandbox demo environment."""
    from app.core.public_service.demo_seed import demo_seed_manager

    return demo_seed_manager.reset_demo()


@router.get("/verification-lab")
def get_verification_lab() -> dict[str, Any]:
    """Returns interactive Verification Lab test cases (valid, tampered, wrong audience, revoked, expired)."""
    from app.core.verification_hardening.verification_lab import VerificationLabService

    lab_svc = VerificationLabService()
    test_cases = lab_svc.run_all_lab_tests()
    return {
        "status": "success",
        "total_tests": len(test_cases),
        "tests": [
            {
                "test_id": tc.test_id,
                "test_name": tc.name,
                "description": tc.description,
                "is_valid": tc.actual_result.is_valid,
                "status": tc.actual_result.status,
                "failure_reason": tc.actual_result.reason or tc.actual_result.failed_check,
                "failed_check": tc.actual_result.failed_check,
                "digest_computed": tc.actual_result.digest_computed,
                "expected_digest": tc.actual_result.expected_digest,
            }
            for tc in test_cases
        ],
    }


@router.get("/demo/state")
def get_demo_state() -> dict[str, Any]:
    """Returns the current deterministic demo state and credentials."""
    from app.core.public_service.demo_seed import demo_seed_manager

    state = demo_seed_manager.get_seed_state()
    return {
        "citizen_account_id": state.citizen_account_id,
        "citizen_name": state.citizen_name,
        "service_id": state.service_id,
        "service_name": state.service_name,
        "organization_id": state.organization_id,
        "organization_name": state.organization_name,
        "valid_proof_id": state.valid_proof_id,
        "tampered_proof_id": state.tampered_proof_id,
        "expired_proof_id": state.expired_proof_id,
        "revoked_proof_id": state.revoked_proof_id,
        "credentials": state.credentials,
    }
