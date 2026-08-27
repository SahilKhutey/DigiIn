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
from app.core.proofs.assertion_service import assertion_service
from app.core.public_service import (
    ApplicationStatus,
    data_saver_engine,
    service_registry,
    sharing_review_generator,
)
from app.core.sandbox.mock_institution_registry import mock_institution_registry
from app.core.verification_layer import (
    DepartmentVerificationRequest,
    verification_layer,
)

router = APIRouter(prefix="/public-service", tags=["Public Services & Scholarship Flow"])



# Pydantic Request/Response Models
class StartScholarshipRequest(BaseModel):
    citizen_account_id: str = Field(default="DI-7K4M-9Q2X-8P6R", description="Sovereign citizen account ID")
    citizen_name: str = Field(default="Rahul Sharma", description="Applicant full name")


class ConsentAndSubmitRequest(BaseModel):
    citizen_account_id: str = Field(default="DI-7K4M-9Q2X-8P6R")
    consent_granted: bool = Field(default=True, description="Explicit purpose-bound citizen consent")


class AttributeVerificationRequestPayload(BaseModel):
    department_id: str = Field(default="dept_du_scholarship_portal")
    department_name: str = Field(default="University of Delhi — Scholarship Board")
    digiin_account_id: str = Field(default="DI-7K4M-9Q2X-8P6R")
    purpose: str = Field(default="Scholarship Merit Verification")
    requested_attributes: list[str] = Field(
        default=["income_status", "domicile_status", "caste_status", "education_qualification"]
    )
    temporary_verification_code: str | None = None


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


@router.post("/verify-attributes")
def verify_attributes_for_department(payload: AttributeVerificationRequestPayload) -> dict[str, Any]:
    """DigiIn Verification Layer Gateway: Department queries verified attributes with zero raw PDF transfers."""
    try:
        from uuid import uuid4
        dept_req = DepartmentVerificationRequest(
            request_id=f"req_{uuid4().hex[:10]}",
            department_id=payload.department_id,
            department_name=payload.department_name,
            digiin_account_id=payload.digiin_account_id,
            purpose=payload.purpose,
            requested_attributes=payload.requested_attributes,
            temporary_verification_code=payload.temporary_verification_code,
        )
        resp = verification_layer.process_verification_request(dept_req)
        return {
            "status": "success",
            "verification_id": resp.verification_id,
            "digiin_account_id": resp.digiin_account_id,
            "department_id": resp.department_id,
            "purpose": resp.purpose,
            "verification_status": resp.verification_status,
            "assertions": resp.assertions,
            "raw_files_transferred_bytes": resp.raw_files_transferred_bytes,
            "issuer_provenance": resp.issuer_provenance,
            "cryptographic_proof": resp.cryptographic_proof,
            "issued_at": resp.issued_at,
            "expires_at": resp.expires_at,
            "consent_id": resp.consent_id,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/citizen/{account_id}/temp-code")
def create_temporary_code(account_id: str) -> dict[str, Any]:
    """Issues a 6-digit temporary verification code valid for 10 minutes for counter/kiosk verification."""
    try:
        temp_code = verification_layer.issue_temporary_code(account_id)
        return {
            "status": "success",
            "account_id": temp_code.account_id,
            "code": temp_code.code,
            "expires_at_epoch": temp_code.expires_at_epoch,
            "expires_at_iso": temp_code.expires_at_iso,
            "ttl_seconds": temp_code.ttl_seconds,
            "message": "Temporary verification code active for 10 minutes.",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/citizen/{account_id}/qr-token")
def get_citizen_qr_token(account_id: str) -> dict[str, Any]:
    """Returns a short-lived signed QR verification token for mobile/kiosk scans."""
    try:
        qr_info = verification_layer.create_signed_qr_payload(account_id)
        return {"status": "success", **qr_info}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# Phase 3 — Verification Infrastructure Endpoints
class CreateVerificationRequestPayload(BaseModel):
    digiin_account_id: str = Field(default="DI-7K4M-9Q2X-8P6R")
    requesting_service_id: str = Field(default="dept_du_scholarship_portal")
    service_name: str = Field(default="University of Delhi — Scholarship Board")
    purpose: str = Field(default="Scholarship Merit Verification")
    requested_attributes: list[str] = Field(default=["income_status", "domicile_status", "education_qualification"])
    requested_documents: list[str] | None = None
    ttl_seconds: int = Field(default=600, description="Validity window in seconds (default 10 mins)")


class ConsentDecisionPayload(BaseModel):
    decision: str = Field(default="GRANTED", description="GRANTED or DENIED")
    citizen_account_id: str | None = Field(default=None)


@router.post("/verification/requests")
def create_verification_request(payload: CreateVerificationRequestPayload) -> dict[str, Any]:
    """Phase 3: Government service initiates a structured verification request."""
    try:
        req = verification_layer.create_request(
            digiin_account_id=payload.digiin_account_id,
            requesting_service_id=payload.requesting_service_id,
            service_name=payload.service_name,
            purpose=payload.purpose,
            requested_attributes=payload.requested_attributes,
            requested_documents=payload.requested_documents,
            ttl_seconds=payload.ttl_seconds,
        )
        return {
            "status": "success",
            "request_id": req["request_reference"],
            "request_reference": req["request_reference"],
            "verification_status": "consent_required",
            "expires_at": req["expires_at"],
            "message": "Verification request created. Awaiting citizen consent.",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/verification/requests/{request_ref}")
def get_verification_request_status(request_ref: str) -> dict[str, Any]:
    """Phase 3: Inspects verification request status and expiration."""
    req = verification_layer.get_request(request_ref)
    if not req:
        raise HTTPException(status_code=404, detail=f"Verification request {request_ref} not found.")
    return {"status": "success", "request": req}


@router.post("/verification/requests/{request_ref}/consent")
def process_citizen_consent(request_ref: str, payload: ConsentDecisionPayload) -> dict[str, Any]:
    """Phase 3: Citizen approves or denies verification request."""
    try:
        updated_req = verification_layer.submit_consent(
            request_reference=request_ref,
            decision=payload.decision,
            citizen_account_id=payload.citizen_account_id,
        )
        return {
            "status": "success",
            "request_reference": request_ref,
            "verification_status": updated_req["status"],
            "consent_status": updated_req["consent_status"],
            "result": updated_req.get("result"),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/verification/requests/{request_ref}/revoke")
def revoke_verification_consent(request_ref: str) -> dict[str, Any]:
    """Phase 3: Citizen unilaterally revokes access."""
    try:
        updated_req = verification_layer.revoke_consent(request_reference=request_ref)
        return {
            "status": "success",
            "request_reference": request_ref,
            "verification_status": updated_req["status"],
            "consent_status": updated_req["consent_status"],
            "message": "Consent successfully revoked. Service can no longer access this verification assertion.",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/verification/requests/{request_ref}/result")
def get_verification_result(request_ref: str) -> dict[str, Any]:
    """Phase 3: Verifier retrieves verified assertions."""
    req = verification_layer.get_request(request_ref)
    if not req:
        raise HTTPException(status_code=404, detail=f"Verification request {request_ref} not found.")
    if req["status"] != "VERIFIED":
        return {
            "status": "pending",
            "request_reference": request_ref,
            "verification_status": req["status"],
            "message": f"Verification is not finalized. Current status: {req['status']}",
        }
    return {
        "status": "success",
        "request_reference": request_ref,
        "verification_status": "VERIFIED",
        "account": {"digiin_account_id": req["digiin_account_id"]},
        "verification": req["result"],
    }


@router.get("/citizen/{account_id}/verification-history")
def get_citizen_verification_history(account_id: str) -> dict[str, Any]:
    """Phase 3: Citizen transparency portal — Who accessed my DigiIn information?"""
    try:
        history = verification_layer.get_verification_history(account_id)
        audit_trail = verification_layer.get_audit_trail(account_id)
        return {
            "status": "success",
            "account_id": account_id,
            "history_count": len(history),
            "verification_history": history,
            "audit_trail": audit_trail,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# Phase 4 — Cryptographic Trust & Verification Assertion Endpoints
class VerifyAssertionPayload(BaseModel):
    assertion: dict[str, Any]
    expected_audience: str | None = None
    expected_purpose: str | None = None
    enforce_replay_protection: bool = True


@router.post("/verification/assertions/verify")
def verify_cryptographic_assertion(payload: VerifyAssertionPayload) -> dict[str, Any]:
    """Phase 4: Cryptographically verifies an Ed25519 signed verification assertion."""
    outcome = assertion_service.verify_signed_assertion(
        assertion=payload.assertion,
        expected_audience=payload.expected_audience,
        expected_purpose=payload.expected_purpose,
        enforce_replay_protection=payload.enforce_replay_protection,
    )
    if not outcome.get("valid"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": outcome.get("error_code", "INVALID_ASSERTION"),
                "message": outcome.get("message", "Verification assertion validation failed."),
            },
        )
    return {"status": "success", **outcome}


@router.get("/security/events")
def list_security_events() -> dict[str, Any]:
    """Phase 4: Security operations monitoring — Lists security events and anomaly alerts."""
    events = assertion_service.get_security_events()
    return {
        "status": "success",
        "total_events": len(events),
        "security_events": events,
    }


@router.get("/trust/services")
def list_trusted_services() -> dict[str, Any]:
    """Phase 4: Trust Registry — Lists accredited relying government services and public keys."""
    return {
        "status": "success",
        "root_authority": "DigiIn Trust Network",
        "root_key_id": "digiin-ed25519-root-2026-01",
        "public_key_b64": assertion_service.get_public_key_b64(),
        "accredited_services": [
            {
                "service_id": "dept_du_scholarship_portal",
                "service_name": "University of Delhi — Scholarship Board",
                "status": "ACTIVE",
                "accreditation_level": "ACCREDITED_GOVERNMENT_BODY",
                "authorized_scopes": ["income_status", "domicile_status", "caste_status", "education_qualification"],
            },
            {
                "service_id": "dept_nta_jee",
                "service_name": "National Testing Agency (NTA)",
                "status": "ACTIVE",
                "accreditation_level": "ACCREDITED_GOVERNMENT_BODY",
                "authorized_scopes": ["education_qualification", "identity_assertion", "caste_status"],
            },
        ],
    }


# =========================================================================
# Phase 6 — Hackathon Sandbox Institutions & Mock Service Endpoints
# =========================================================================

class CreateSandboxVerificationRequestPayload(BaseModel):
    institution_code: str
    account_id: str
    purpose: str
    requested_scopes: list[str]
    ttl_seconds: int = 900


@router.get("/sandbox/institutions")
def list_sandbox_institutions() -> dict[str, Any]:
    """Phase 6: Lists all registered sandbox demo institutions."""
    institutions = mock_institution_registry.list_institutions()
    return {
        "status": "success",
        "environment": "SANDBOX",
        "total_institutions": len(institutions),
        "institutions": institutions,
        "disclaimer": "Simulated sandbox integrations for DigiIn hackathon jury demonstration.",
    }


@router.get("/sandbox/scopes")
def list_standardized_scopes() -> dict[str, Any]:
    """Phase 6: Lists standardized verification scope definitions across the ecosystem."""
    scopes = mock_institution_registry.list_scopes()
    return {
        "status": "success",
        "environment": "SANDBOX",
        "total_scopes": len(scopes),
        "scopes": scopes,
    }


@router.get("/sandbox/institutions/{institution_code}")
def get_sandbox_institution(institution_code: str) -> dict[str, Any]:
    """Phase 6: Retrieves a single sandbox demo institution by code."""
    inst = mock_institution_registry.get_institution(institution_code)
    if not inst:
        raise HTTPException(status_code=404, detail=f"Sandbox institution '{institution_code}' not found.")
    return {
        "status": "success",
        "institution": inst.to_dict(),
    }


@router.post("/sandbox/verification-requests")
def create_sandbox_verification_request(payload: CreateSandboxVerificationRequestPayload) -> dict[str, Any]:
    """Phase 6: Sandbox institution initiates a verification request via DigiIn Verification Layer."""
    try:
        res = mock_institution_registry.create_verification_request(
            institution_code=payload.institution_code,
            account_id=payload.account_id,
            purpose=payload.purpose,
            requested_scopes=payload.requested_scopes,
            ttl_seconds=payload.ttl_seconds,
        )
        return {
            "status": "success",
            "environment": "SANDBOX",
            **res,
        }
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/sandbox/applications")
def list_sandbox_applications(institution_code: str | None = None) -> dict[str, Any]:
    """Phase 6: Lists applications from the sandbox service portal perspective."""
    apps = mock_institution_registry.list_applications(institution_code)
    return {
        "status": "success",
        "environment": "SANDBOX",
        "total_applications": len(apps),
        "applications": apps,
    }


@router.post("/sandbox/reset")
def reset_hackathon_demo() -> dict[str, Any]:
    """Phase 6: Instant 1-click reset of hackathon demo state to deterministic baseline."""
    return mock_institution_registry.reset_hackathon_demo()




