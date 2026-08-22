"""DigiIn modular-monolith API entry point."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


from app.domain.models import (
    ConsentPreview,
    ConsentRecord,
    CorrectionRequestCreate,
    CorrectionRequestRecord,
    CorrectionReviewDecision,
    DirectUploadPayload,
    DocumentOption,
    DocumentUploadRequest,
    DocumentVersionRecord,
    DomainEvent,
    EkycMatchDemographicsRequest,
    EkycMatchResult,
    EkycOtpRequest,
    EkycOtpResponse,
    EkycVerifyRequest,
    EkycVerifyResponse,
    EvidenceComparisonDetail,
    GovernmentReviewDecision,
    IssuerHealth,
    JwksResponse,
    PipelineUploadResponse,
    PlatformSnapshot,
    ProofTokenIntrospection,
    ProofTokenIntrospectionRequest,
    RevokeConsentPayload,
    ScenarioSummary,
    StudentDemoResult,
    SupportSafeSummary,
    TransactionDiagnosis,
    UploadedDocument,
    VerificationAuthorization,
    VerificationCase,
    VerificationRequestCreate,
    VerificationRequestRecord,
    VerificationResult,
    VerifierQueueId,
    VerifierQueueSummary,
    WalletDocument,
)
from app.services.crypto import get_public_jwks
from app.services.ekyc import (
    calculate_demographics_match,
    generate_ekyc_otp,
    verify_ekyc_otp_and_match,
    MOCK_UIDAI_IDENTITIES,
)

from app.services.platform import (
    classify_document,
    create_correction_request,
    create_verification_case,
    decide_correction_request,
    decide_verification_case,
    get_case_evidence_comparison,
    get_correction,
    get_document_versions,
    get_wallet_documents,
    list_corrections,
    list_verifier_cases,
    list_verifier_queues,
    platform_snapshot,
    run_student_demo,
    upload_and_classify_pipeline,
    upload_document,
)

from app.services.catalogue import get_document, search_documents
from app.services.recovery import generate_support_summary, get_diagnosis, list_scenarios
from app.services.trust import consent_preview, issuer_health
from app.services.verification import (
    authorize_verification_request,
    create_verification_request,
    demo_exam_request,
    get_verification_request,
    get_verification_result,
    introspect_token,
    list_consents,
    list_verification_requests,
    result_for_request,
    revoke_verification_consent,
)



from app.db.session import check_db_health, init_db

# Initialize database tables and initial seed fixtures on module load / startup
init_db()

app = FastAPI(title="DigiIn Prototype API", version="0.4.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, Any]:
    db_health = check_db_health()
    return {
        "status": "ok",
        "service": "digiin-api",
        "mode": "persistent-relational",
        "database": db_health,
    }


@app.get("/.well-known/jwks.json", response_model=JwksResponse)
@app.get("/api/v1/.well-known/jwks.json", response_model=JwksResponse)
def jwks() -> JwksResponse:
    """RFC 7517 JSON Web Key Set discovery endpoint for offline third-party proof verification."""
    return JwksResponse(**get_public_jwks())




@app.get("/api/v1/documents", response_model=list[DocumentOption])
def list_documents(q: str = Query(default="", max_length=80)) -> list[DocumentOption]:
    """Intent-first search over the safe mock catalogue."""
    return search_documents(q)


@app.get("/api/v1/documents/{document_id}", response_model=DocumentOption)
def read_document(document_id: str) -> DocumentOption:
    document = get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document type not found")
    return document


@app.get("/api/v1/wallet/documents", response_model=list[WalletDocument])
def list_wallet_documents(subject_id: str = Query(default="subj_demo_5c7b90")) -> list[WalletDocument]:
    """Retrieve all citizen wallet documents with full 5-signal trust models."""
    return get_wallet_documents(subject_id)



@app.get("/api/v1/scenarios", response_model=list[ScenarioSummary])
def scenarios() -> list[ScenarioSummary]:
    return list_scenarios()


@app.get("/api/v1/transactions/{transaction_id}/diagnosis", response_model=TransactionDiagnosis)
def transaction_diagnosis(transaction_id: str) -> TransactionDiagnosis:
    diagnosis = get_diagnosis(transaction_id)
    if diagnosis is None:
        raise HTTPException(status_code=404, detail="Transaction diagnosis not found")
    return diagnosis


@app.get("/api/v1/transactions/{transaction_id}/support-summary", response_model=SupportSafeSummary)
def transaction_support_summary(transaction_id: str) -> SupportSafeSummary:
    """Generate a printable, PII-free facilitation report with an opaque support code."""
    summary = generate_support_summary(transaction_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Transaction scenario not found")
    return summary



@app.get("/api/v1/diagnostics/{scenario_id}", response_model=TransactionDiagnosis, deprecated=True)
def legacy_diagnostic(scenario_id: str) -> TransactionDiagnosis:
    """Compatibility route; use the transaction diagnosis endpoint for new clients."""
    return transaction_diagnosis(scenario_id)


@app.post("/api/v1/transactions/{transaction_id}/retry", response_model=TransactionDiagnosis)
def targeted_retry(transaction_id: str) -> TransactionDiagnosis:
    """Prototype-only targeted retry; no external system is contacted."""
    return transaction_diagnosis(transaction_id)


@app.post("/api/v1/diagnostics/{scenario_id}/retry", response_model=TransactionDiagnosis, deprecated=True)
def legacy_retry(scenario_id: str) -> TransactionDiagnosis:
    return targeted_retry(scenario_id)


@app.get("/api/v1/issuers/health", response_model=list[IssuerHealth])
def list_issuer_health() -> list[IssuerHealth]:
    return issuer_health()


@app.get("/api/v1/consents/preview", response_model=ConsentPreview)
def get_consent_preview() -> ConsentPreview:
    return consent_preview()


@app.post("/api/v1/verification/request", response_model=VerificationRequestRecord)
def create_proof_request(payload: VerificationRequestCreate) -> VerificationRequestRecord:
    """Create a purpose-bound verification request from a requester portal."""
    return create_verification_request(payload)


@app.post("/api/v1/verification/request/demo-exam", response_model=VerificationRequestRecord)
def create_demo_exam_request() -> VerificationRequestRecord:
    """Create a synthetic multi-credential exam eligibility request."""
    return create_verification_request(demo_exam_request())


@app.get("/api/v1/verification/request", response_model=list[VerificationRequestRecord])
def verification_requests() -> list[VerificationRequestRecord]:
    return list_verification_requests()


@app.get("/api/v1/verification/request/{request_id}", response_model=VerificationRequestRecord)
def read_verification_request(request_id: str) -> VerificationRequestRecord:
    request = get_verification_request(request_id)
    if request is None:
        raise HTTPException(status_code=404, detail="Verification request not found")
    return request


@app.post("/api/v1/verification/request/{request_id}/authorize", response_model=VerificationResult)
def authorize_proof_request(
    request_id: str, payload: VerificationAuthorization
) -> VerificationResult:
    result = authorize_verification_request(request_id, payload)
    if result is None:
        raise HTTPException(status_code=404, detail="Verification request not found")
    return result


@app.get("/api/v1/verification/request/{request_id}/status")
def verification_request_status(request_id: str) -> dict[str, str]:
    request = get_verification_request(request_id)
    if request is None:
        raise HTTPException(status_code=404, detail="Verification request not found")
    result = result_for_request(request_id)
    return {
        "requestId": request.requestId,
        "requestStatus": request.status,
        "verificationId": result.verificationId if result else "",
        "verificationStatus": result.status if result else "PENDING",
    }


@app.get("/api/v1/verification/result/{verification_id}", response_model=VerificationResult)
def read_verification_result(verification_id: str) -> VerificationResult:
    result = get_verification_result(verification_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Verification result not found")
    return result


@app.get("/api/v1/verification/token/{verification_id}")
def read_verification_token(verification_id: str) -> dict[str, str]:
    result = get_verification_result(verification_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Verification result not found")
    return {
        "verificationId": result.verificationId,
        "type": result.proof.type,
        "token": result.proof.token,
        "algorithm": result.proof.algorithm,
    }


@app.post("/api/v1/verification/introspect", response_model=ProofTokenIntrospection)
def introspect_proof_token(
    payload: ProofTokenIntrospectionRequest,
) -> ProofTokenIntrospection:
    return introspect_token(payload.token, payload.audience, payload.nonce)


@app.get("/api/v1/consent", response_model=list[ConsentRecord])
def get_consents(subject_id: str = Query(default="subj_demo_5c7b90")) -> list[ConsentRecord]:
    """Retrieve all active, revoked, and historical consents for a citizen."""
    return list_consents(subject_id)


@app.post("/api/v1/consent/{verification_id}/revoke", response_model=ConsentRecord)
def revoke_consent(
    verification_id: str,
    payload: RevokeConsentPayload,
    subject_id: str = Query(default="subj_demo_5c7b90"),
) -> ConsentRecord:
    """Cryptographically revokes an active proof token issued to a relying party."""
    updated = revoke_verification_consent(verification_id, subject_id, payload.reason)
    if updated is None:
        raise HTTPException(status_code=404, detail="Verification consent not found")
    return updated


@app.get("/api/v1/audit/events", response_model=list[DomainEvent])
def get_audit_events(
    event_type: str | None = Query(default=None),
    aggregate_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[DomainEvent]:
    """Retrieves full filterable platform audit trail of sovereign domain events."""
    snapshot = platform_snapshot()
    events = snapshot.events
    if event_type:
        events = [e for e in events if e.type == event_type]
    if aggregate_id:
        events = [e for e in events if e.aggregateId == aggregate_id]
    return events[-limit:]


@app.get("/api/v1/platform/snapshot", response_model=PlatformSnapshot)
def read_platform_snapshot() -> PlatformSnapshot:
    """Read the current synthetic platform state: flags, policies, integrations and events."""
    return platform_snapshot()



@app.post("/api/v1/documents/upload", response_model=UploadedDocument)
def create_uploaded_document(payload: DocumentUploadRequest) -> UploadedDocument:
    """Create citizen-uploaded document metadata; no real file is accepted in the prototype."""
    return upload_document(payload)


@app.post("/api/v1/documents/upload-pipeline", response_model=PipelineUploadResponse)
def execute_upload_pipeline(payload: DirectUploadPayload) -> PipelineUploadResponse:
    """Ingest document, extract OCR entities, compute hash, and enqueue for verification review."""
    return upload_and_classify_pipeline(payload)



@app.post("/api/v1/documents/{document_id}/classify", response_model=UploadedDocument)
def classify_uploaded_document(document_id: str) -> UploadedDocument:
    document = classify_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Uploaded document not found")
    return document


@app.post("/api/v1/documents/{document_id}/verification-case", response_model=VerificationCase)
def open_verification_case(document_id: str) -> VerificationCase:
    case = create_verification_case(document_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Uploaded document not found")
    return case


@app.post("/api/v1/verification/cases/{case_id}/decision", response_model=VerificationCase)
def decide_case(case_id: str, payload: GovernmentReviewDecision) -> VerificationCase:
    case = decide_verification_case(case_id, payload)
    if case is None:
        raise HTTPException(status_code=404, detail="Verification case not found")
    return case


@app.post("/api/v1/documents/{document_id}/corrections", response_model=CorrectionRequestRecord)
def request_document_correction(
    document_id: str, payload: CorrectionRequestCreate
) -> CorrectionRequestRecord:
    """Submit a formal citizen correction request for an official or uploaded document."""
    request = create_correction_request(document_id, payload)
    if request is None:
        raise HTTPException(status_code=404, detail="Target document not found")
    return request


@app.get("/api/v1/documents/{document_id}/corrections", response_model=list[CorrectionRequestRecord])
def get_corrections_for_document(document_id: str) -> list[CorrectionRequestRecord]:
    """List all correction requests associated with a specific document."""
    return list_corrections(document_id)


@app.get("/api/v1/documents/{document_id}/versions", response_model=list[DocumentVersionRecord])
def get_versions_for_document(document_id: str) -> list[DocumentVersionRecord]:
    """Retrieve the complete, immutable version history chain for a document."""
    return get_document_versions(document_id)


@app.get("/api/v1/corrections", response_model=list[CorrectionRequestRecord])
def get_all_corrections() -> list[CorrectionRequestRecord]:
    """List all platform correction requests across all queues."""
    return list_corrections()


@app.get("/api/v1/corrections/{request_id}", response_model=CorrectionRequestRecord)
def read_correction_request(request_id: str) -> CorrectionRequestRecord:
    request = get_correction(request_id)
    if request is None:
        raise HTTPException(status_code=404, detail="Correction request not found")
    return request


@app.post("/api/v1/corrections/{request_id}/decision", response_model=CorrectionRequestRecord)
def review_correction(
    request_id: str, payload: CorrectionReviewDecision
) -> CorrectionRequestRecord:
    """Record an authorized officer decision on a correction request and issue a new version if approved."""
    request = decide_correction_request(request_id, payload)
    if request is None:
        raise HTTPException(status_code=404, detail="Correction request or document not found")
    return request


@app.post("/api/v1/platform/demo/student", response_model=StudentDemoResult)
def run_student_vertical_slice() -> StudentDemoResult:
    """Run the canonical student upload -> government verification -> requester proof demo."""
    return run_student_demo()


@app.get("/api/v1/verifier/queues", response_model=list[VerifierQueueSummary])
def verifier_queues() -> list[VerifierQueueSummary]:
    """List multi-tenant verifier queues with live pending and verified counts."""
    return list_verifier_queues()


@app.get("/api/v1/verifier/cases", response_model=list[VerificationCase])
def verifier_cases(
    queue_id: VerifierQueueId | None = Query(default=None),
    status: str | None = Query(default=None),
) -> list[VerificationCase]:
    """List verification cases with optional department queue and status filters."""
    return list_verifier_cases(queue_id, status)


@app.get("/api/v1/verifier/cases/{case_id}/comparison", response_model=EvidenceComparisonDetail)
def verifier_case_comparison(case_id: str) -> EvidenceComparisonDetail:
    """Fetch side-by-side evidence diff comparison for a specific verification case."""
    comparison = get_case_evidence_comparison(case_id)
    if comparison is None:
        raise HTTPException(status_code=404, detail="Verification case or document not found")
    return comparison


@app.post("/api/v1/verifier/cases/{case_id}/decision", response_model=VerificationCase)
def submit_verifier_decision(
    case_id: str, payload: GovernmentReviewDecision
) -> VerificationCase:
    """Record an official government verifier decision (Verify, Reject, Request Evidence, Transfer)."""
    case = decide_verification_case(case_id, payload)
    if case is None:
        raise HTTPException(status_code=404, detail="Verification case not found")
    return case


# --- Aadhaar / eKYC Mock Gateway Endpoints ---


@app.post("/api/v1/ekyc/generate-otp", response_model=EkycOtpResponse)
def ekyc_generate_otp(payload: EkycOtpRequest) -> EkycOtpResponse:
    """Generate simulated Aadhaar eKYC OTP sent to citizen's registered mobile number."""
    return generate_ekyc_otp(payload.aadhaarRef, payload.purpose)


@app.post("/api/v1/ekyc/verify-otp", response_model=EkycVerifyResponse)
def ekyc_verify_otp(payload: EkycVerifyRequest) -> EkycVerifyResponse:
    """Verify 6-digit eKYC OTP, produce signed Ed25519 assertion, and elevate document trust level."""
    return verify_ekyc_otp_and_match(
        txn_id=payload.txnId,
        otp=payload.otp,
        document_id=payload.documentId,
    )



@app.post("/api/v1/ekyc/match-demographics", response_model=EkycMatchResult)
def ekyc_match_demographics(payload: EkycMatchDemographicsRequest) -> EkycMatchResult:
    """Perform 1:1 fuzzy demographic match between document claims and UIDAI central registry fixtures."""
    clean_ref = payload.aadhaarRef.strip().replace(" ", "").replace("-", "")
    identity = MOCK_UIDAI_IDENTITIES.get(
        payload.aadhaarRef,
        MOCK_UIDAI_IDENTITIES.get(clean_ref, {"name": "SAHIL KHUTEY", "dob": "2006-05-14", "state": "Chhattisgarh"}),
    )

    return calculate_demographics_match(
        claimed_name=payload.claimedName,
        official_name=identity["name"],
        claimed_dob=payload.claimedDob,
        official_dob=identity.get("dob"),
        claimed_state=payload.claimedState,
        official_state=identity.get("state"),
    )



