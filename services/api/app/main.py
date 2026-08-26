"""DigiIn modular-monolith API entry point."""

from __future__ import annotations

import os
import time
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

import app.db.repository as repo
from app.api.middleware.security_pipeline import SecurityPipelineMiddleware
from app.api.v1 import (
    auth as auth_router,
)
from app.api.v1 import (
    citizen as citizen_router,
)
from app.api.v1 import (
    demo as demo_router,
)
from app.api.v1 import (
    documents as documents_router,
)
from app.api.v1 import (
    government as government_router,
)
from app.api.v1 import (
    health as health_router,
)
from app.api.v1 import (
    jobs as jobs_router,
)
from app.api.v1 import (
    ops as ops_router,
)
from app.api.v1 import (
    proofs as proofs_router,
)
from app.api.v1 import (
    providers as providers_router,
)
from app.api.v1 import (
    public_service as public_service_router,
)
from app.api.v1 import (
    review as review_router,
)
from app.api.v1 import (
    verification_intelligence as intelligence_router,
)
from app.crypto.proofs import (
    Proof,
    _b64,
    generate_keypair,
    sign_proof,
    verify_proof,
)
from app.db.session import check_db_health, init_db
from app.domain.credential_models import (
    CredentialResponse,
    IssueCredentialRequest,
    RevokeCredentialRequest,
    VerificationDecision,
    VerificationStatus,
    VerifiedClaim,
    VerifiedClaimSchema,
    VerifyCredentialRequest,
    VerifyCredentialResponse,
)
from app.domain.gateway_models import (
    Consent as GatewayConsent,
)
from app.domain.gateway_models import (
    CreateGatewayVerificationRequest,
    GatewayConsentApproveRequest,
    GatewayConsentResponse,
    GatewayEvaluateResponse,
    GatewayVerificationRequestResponse,
    ProofSchema,
    RequestStatus,
    VerifyProofRequest,
    VerifyProofResponse,
)
from app.domain.gateway_models import (
    VerificationRequest as GatewayVerificationRequest,
)
from app.domain.models import (
    AuthSendOtpRequest,
    AuthSendOtpResponse,
    AuthTokenPairResponse,
    AuthVerifyOtpRequest,
    ConsentPreview,
    ConsentRecord,
    CorrectionRequestCreate,
    CorrectionRequestRecord,
    CorrectionReviewDecision,
    DirectUploadPayload,
    DocumentClaimRecord,
    DocumentOption,
    DocumentUploadJobResponse,
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
    ProcessingJobRecord,
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
from app.services.catalogue import get_document, search_documents
from app.services.credential_issuer import CredentialIssuanceError, CredentialIssuer
from app.services.credential_verifier import CredentialVerifier
from app.services.crypto import get_public_jwks
from app.services.disclosure_policy import DisclosurePolicyError
from app.services.ekyc import (
    MOCK_UIDAI_IDENTITIES,
    calculate_demographics_match,
    generate_ekyc_otp,
    verify_ekyc_otp_and_match,
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
from app.services.verification_gateway import VerificationGateway

# Initialize database tables and initial seed fixtures on module load / startup
init_db()

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Hardened security headers, correlation ID injection, and microsecond server timing middleware."""

    async def dispatch(self, request: Request, call_next):  # type: ignore
        start_time = time.perf_counter()
        req_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"
        response: Response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        response.headers["X-Request-ID"] = req_id
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
        response.headers["Server-Timing"] = f"total;dur={duration_ms:.2f}"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response



app = FastAPI(title="DigiLocker X API", version="0.5.0")
app.add_middleware(SecurityHeadersMiddleware)
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
if allowed_origins_env:
    cors_origins.extend([o.strip() for o in allowed_origins_env.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"^https:\/\/.*(vercel\.app|onrender\.com|digiin\..*|localhost:[0-9]+)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phase 8 — Security Pipeline Middleware (request ID, security headers, threat detection)
app.add_middleware(SecurityPipelineMiddleware)


app.include_router(health_router.router, prefix="/api/v1")
app.include_router(ops_router.router, prefix="/api/v1")
app.include_router(demo_router.router, prefix="/api/v1")
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(citizen_router.router, prefix="/api/v1")
app.include_router(documents_router.router, prefix="/api/v1")
app.include_router(jobs_router.router, prefix="/api/v1")
app.include_router(government_router.router, prefix="/api/v1")
app.include_router(intelligence_router.router, prefix="/api/v1")
app.include_router(proofs_router.router, prefix="/api/v1")
app.include_router(providers_router.router, prefix="/api/v1")
app.include_router(public_service_router.router, prefix="/api/v1")
app.include_router(review_router.router, prefix="/api/v1")

# Bootstrap Phase 7 mock providers (development / sandbox only)
from app.integrations.mock_providers import register_mock_providers  # noqa: E402

register_mock_providers()




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


@app.post("/api/v1/auth/otp/send", response_model=AuthSendOtpResponse)
def send_auth_otp(payload: AuthSendOtpRequest) -> AuthSendOtpResponse:
    """Passwordless mobile OTP challenge generation."""
    phone = payload.phoneNumber.strip()
    masked = f"+91 {phone[-10:-4]}****{phone[-2:]}" if len(phone) >= 10 else "+91 98****10"
    challenge_id = f"otp_ch_{phone[-4:] if len(phone)>=4 else 'demo'}"
    return AuthSendOtpResponse(
        challengeId=challenge_id,
        maskedPhone=masked,
        expiresInSeconds=300,
        demoOtpHint="123456",
        message="OTP challenge dispatched. In prototype mode, use 123456.",
    )


@app.post("/api/v1/auth/otp/verify", response_model=AuthTokenPairResponse)
def verify_auth_otp(payload: AuthVerifyOtpRequest) -> AuthTokenPairResponse:
    """Verify OTP challenge and return sovereign session tokens with opaque DigiIn Account ID."""
    from app.integrations.auth import get_auth_provider
    provider = get_auth_provider()
    try:
        subject = provider.verify_otp(payload.challengeId, payload.otpCode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return AuthTokenPairResponse(
        accessToken="eyJhbGciOiJFZERTQSI...demo_access_token",
        refreshToken="rft_demo_rotatable_token_9f8a",
        tokenType="Bearer",
        expiresIn=900,
        subjectId=subject.subject_id,
        accountId=subject.account_id,
        role=subject.role,
    )


@app.get("/api/v1/issuers")
def list_issuers() -> list[dict[str, Any]]:
    """List registered government issuer adapters and capabilities."""
    from app.integrations.issuer import issuer_registry

    return [
        {
            "issuerId": a.issuer_id,
            "name": a.name,
            "health": a.health().model_dump(by_alias=True, mode="json"),
            "capabilities": list(a.capabilities()),
        }
        for a in issuer_registry.list_all()
    ]





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
@app.post("/api/v1/verification/requests", response_model=VerificationRequestRecord)
def create_proof_request(payload: VerificationRequestCreate) -> VerificationRequestRecord:
    """Create a purpose-bound verification request from a requester portal."""
    return create_verification_request(payload)


@app.post("/api/v1/verification/request/demo-exam", response_model=VerificationRequestRecord)
def create_demo_exam_request() -> VerificationRequestRecord:
    """Create a synthetic multi-credential exam eligibility request."""
    return create_verification_request(demo_exam_request())


@app.get("/api/v1/verification/request", response_model=list[VerificationRequestRecord])
@app.get("/api/v1/verification/requests", response_model=list[VerificationRequestRecord])
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


@app.post("/api/v1/documents/ingest", response_model=DocumentUploadJobResponse)
async def ingest_document_stream(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: str = Form(default="CLASS_XII"),
    owner_account_id: str = Form(default="DIN-DEMO-0000-0001"),
) -> DocumentUploadJobResponse:
    """Phase 2 multipart document ingestion with streaming SHA-256 and async job queue."""
    from app.services.document_pipeline import execute_processing_job, ingest_document
    try:
        res = ingest_document(
            stream=file.file,
            filename=file.filename or "document.pdf",
            content_type=file.content_type or "application/pdf",
            owner_account_id=owner_account_id,
            document_type_hint=document_type,
        )
        background_tasks.add_task(execute_processing_job, res.processing_job_id)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/documents/jobs/{job_id}", response_model=ProcessingJobRecord)
def get_job_status(job_id: str) -> ProcessingJobRecord:
    """Retrieve async document processing job status, scan details, and OCR claims."""
    from app.db.repository import get_processing_job
    job = get_processing_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Processing job not found")
    return job


@app.post("/api/v1/documents/jobs/{job_id}/process", response_model=ProcessingJobRecord)
def process_job_synchronously(job_id: str) -> ProcessingJobRecord:
    """Synchronously execute document processing pipeline for testing and validation."""
    from app.services.document_pipeline import execute_processing_job
    try:
        return execute_processing_job(job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/v1/documents/{document_id}/claims", response_model=list[DocumentClaimRecord])
def get_document_claims_endpoint(document_id: str) -> list[DocumentClaimRecord]:
    """Retrieve all structured OCR claims extracted for a persistent document."""
    from app.db.repository import get_document_claims
    return get_document_claims(document_id)



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


# --- Phase 4: Credential & Verification Engine Endpoints ---

@app.post("/api/v1/credentials/issue", response_model=CredentialResponse)
def issue_credential(payload: IssueCredentialRequest) -> CredentialResponse:
    """Issue a durable, sovereign DigiIn credential from an approved verification case."""
    decision = VerificationDecision(
        case_id=payload.case_id,
        account_id=payload.account_id,
        status=VerificationStatus.APPROVED,
        decided_by="officer_authorized",
        decided_at=datetime.now(UTC),
    )
    claims = tuple(
        VerifiedClaim(
            claim_type=c.claim_type,
            value=c.value,
            source=c.source,
            verification_level=c.verification_level,
            verified_at=c.verified_at or datetime.now(UTC),
        )
        for c in payload.claims
    )
    try:
        issuer = CredentialIssuer()
        cred = issuer.issue(
            decision=decision,
            credential_type=payload.credential_type,
            issuer=payload.issuer,
            claims=claims,
            expires_at=payload.expires_at,
        )
        repo.save_credential(cred)
        return CredentialResponse(
            credential_id=cred.credential_id,
            account_id=cred.account_id,
            credential_type=cred.credential_type,
            issuer=cred.issuer,
            claims=[
                VerifiedClaimSchema(
                    claim_type=cl.claim_type,
                    value=cl.value,
                    source=cl.source,
                    verification_level=cl.verification_level,
                    verified_at=cl.verified_at,
                )
                for cl in cred.claims
            ],
            issued_at=cred.issued_at,
            expires_at=cred.expires_at,
            status=cred.status.value,
            verification_case_id=cred.verification_case_id,
        )
    except CredentialIssuanceError as err:
        raise HTTPException(status_code=400, detail=str(err))


@app.get("/api/v1/credentials/{credential_id}", response_model=CredentialResponse)
def get_credential(credential_id: str) -> CredentialResponse:
    """Retrieve specific credential by CRD-... identifier."""
    c = repo.get_credential_by_id(credential_id)
    if not c:
        raise HTTPException(status_code=404, detail="Credential not found")
    return CredentialResponse(
        credential_id=c.credential_id,
        account_id=c.account_id,
        credential_type=c.credential_type,
        issuer=c.issuer,
        claims=[
            VerifiedClaimSchema(
                claim_type=cl.claim_type,
                value=cl.value,
                source=cl.source,
                verification_level=cl.verification_level,
                verified_at=cl.verified_at,
            )
            for cl in c.claims
        ],
        issued_at=c.issued_at,
        expires_at=c.expires_at,
        status=c.status.value,
        verification_case_id=c.verification_case_id,
    )


@app.post("/api/v1/credentials/{credential_id}/revoke")
def revoke_credential_endpoint(credential_id: str, payload: RevokeCredentialRequest | None = None) -> dict[str, str]:
    """Revoke an active credential."""
    c = repo.get_credential_by_id(credential_id)
    if not c:
        raise HTTPException(status_code=404, detail="Credential not found")
    repo.revoke_credential(credential_id)
    return {"status": "revoked", "credential_id": credential_id}


@app.post("/api/v1/credentials/verify", response_model=VerifyCredentialResponse)
def verify_credential_endpoint(payload: VerifyCredentialRequest) -> VerifyCredentialResponse:
    """Perform independent state and lifecycle verification of a DigiIn credential."""
    c = repo.get_credential_by_id(payload.credential_id)
    if not c:
        return VerifyCredentialResponse(valid=False, reason="not_found")
    verifier = CredentialVerifier()
    res = verifier.verify(c)
    return VerifyCredentialResponse(**res)


# --- Phase 5: Verification Gateway Endpoints ---

@app.post("/api/v1/gateway/requests", response_model=GatewayVerificationRequestResponse)
def create_gateway_request_endpoint(payload: CreateGatewayVerificationRequest) -> GatewayVerificationRequestResponse:
    """External verifier initiates a purpose-bound request against a DigiIn Account ID."""
    now = datetime.now(UTC)
    req_id = f"REQ-{uuid.uuid4().hex[:12]}"
    exp = now + timedelta(minutes=payload.ttl_minutes)

    req = GatewayVerificationRequest(
        request_id=req_id,
        verifier_id=payload.verifier_id,
        account_id=payload.account_id,
        purpose=payload.purpose,
        requested_claim_types=tuple(payload.requested_claim_types),
        status=RequestStatus.PENDING,
        expires_at=exp,
        created_at=now,
    )
    repo.save_gateway_request(req)
    return GatewayVerificationRequestResponse(
        request_id=req.request_id,
        verifier_id=req.verifier_id,
        account_id=req.account_id,
        purpose=req.purpose,
        requested_claim_types=list(req.requested_claim_types),
        status=req.status.value,
        created_at=req.created_at,
        expires_at=req.expires_at,
    )


@app.get("/api/v1/gateway/requests/{request_id}", response_model=GatewayVerificationRequestResponse)
def get_gateway_request_endpoint(request_id: str) -> GatewayVerificationRequestResponse:
    """Retrieve details of a verification request for citizen approval or verifier status."""
    req = repo.get_gateway_request(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Verification request not found")
    return GatewayVerificationRequestResponse(
        request_id=req.request_id,
        verifier_id=req.verifier_id,
        account_id=req.account_id,
        purpose=req.purpose,
        requested_claim_types=list(req.requested_claim_types),
        status=req.status.value,
        created_at=req.created_at,
        expires_at=req.expires_at,
    )


def _to_utc(dt: datetime | None) -> datetime:
    if dt is None:
        return datetime.now(UTC)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


@app.post("/api/v1/gateway/requests/{request_id}/approve", response_model=GatewayConsentResponse)
def approve_gateway_request_endpoint(
    request_id: str,
    payload: GatewayConsentApproveRequest,
) -> GatewayConsentResponse:
    """Citizen grants purpose-bound consent for a selective subset of requested claims."""
    req = repo.get_gateway_request(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Verification request not found")
    now = datetime.now(UTC)
    if _to_utc(req.expires_at) <= now:
        repo.update_gateway_request_status(request_id, RequestStatus.EXPIRED)
        raise HTTPException(status_code=400, detail="Verification request has expired")

    # Update request status to APPROVED
    repo.update_gateway_request_status(request_id, RequestStatus.APPROVED)

    consent = GatewayConsent(
        consent_id=f"CON-{uuid.uuid4().hex[:12]}",
        request_id=request_id,
        account_id=req.account_id,
        decision="approved",
        approved_claim_types=tuple(payload.approved_claim_types),
        granted_at=now,
        expires_at=now + timedelta(minutes=payload.ttl_minutes),
        revoked_at=None,
    )
    repo.save_gateway_consent(consent)

    return GatewayConsentResponse(
        consent_id=consent.consent_id,
        request_id=consent.request_id,
        account_id=consent.account_id,
        decision=consent.decision,
        approved_claim_types=list(consent.approved_claim_types),
        granted_at=consent.granted_at,
        expires_at=consent.expires_at,
        revoked_at=consent.revoked_at,
    )


@app.post("/api/v1/gateway/requests/{request_id}/deny")
def deny_gateway_request_endpoint(request_id: str) -> dict[str, str]:
    """Citizen denies verification request."""
    req = repo.get_gateway_request(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Verification request not found")
    repo.update_gateway_request_status(request_id, RequestStatus.DENIED)
    return {"status": "denied", "request_id": request_id}


@app.post("/api/v1/gateway/requests/{request_id}/revoke")
def revoke_gateway_request_endpoint(request_id: str) -> dict[str, str]:
    """Citizen revokes prior consent granted for a verification request."""
    req = repo.get_gateway_request(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Verification request not found")
    repo.revoke_gateway_consent(request_id)
    return {"status": "revoked", "request_id": request_id}


# System-level gateway Ed25519 signing keypair
GATEWAY_SIGNING_KEY, GATEWAY_PUBLIC_KEY = generate_keypair()
GATEWAY_KEY_ID = "digiin-ed25519-key-2026"


@app.post("/api/v1/gateway/requests/{request_id}/evaluate", response_model=GatewayEvaluateResponse)
def evaluate_gateway_request_endpoint(request_id: str) -> GatewayEvaluateResponse:
    """Verifier triggers evaluation of approved request against citizen's active credentials."""
    req = repo.get_gateway_request(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Verification request not found")

    consent = repo.get_gateway_consent_by_request(request_id)
    if not consent:
        return GatewayEvaluateResponse(
            valid=False,
            reason="consent_not_granted",
            request_id=request_id,
            purpose=req.purpose,
        )

    # Collect available verified claims from active credentials owned by the account
    creds = repo.list_credentials_for_account(req.account_id)
    active_creds = [c for c in creds if c.status.value == "active"]

    available_claims: dict[str, str] = {}
    for c in active_creds:
        for cl in c.claims:
            available_claims[cl.claim_type] = cl.value

    # Also include identity claims
    id_claims = repo.get_identity_claims(req.account_id)
    for ic in id_claims:
        available_claims[ic.claim_type] = ic.value_reference

    gateway = VerificationGateway()
    now = datetime.now(UTC)
    try:
        eval_result = gateway.evaluate(req, consent, available_claims)
        is_valid = eval_result.get("valid", False)
        proof_schema = None
        if is_valid:
            now_ts = int(now.timestamp())
            exp_ts = int((now + timedelta(minutes=15)).timestamp())
            proof = sign_proof(
                proof_id=f"PRF-{uuid.uuid4().hex[:12]}",
                issuer="digiin",
                audience=req.verifier_id,
                nonce=req.request_id,
                claims=eval_result.get("claims", {}),
                key_id=GATEWAY_KEY_ID,
                private_key=GATEWAY_SIGNING_KEY,
                expires_at=exp_ts,
                issued_at=now_ts,
            )
            proof_schema = ProofSchema(
                proof_id=proof.proof_id,
                issuer=proof.issuer,
                audience=proof.audience,
                issued_at=proof.issued_at,
                expires_at=proof.expires_at,
                nonce=proof.nonce,
                claims=proof.claims,
                key_id=proof.key_id,
                signature=proof.signature,
            )

        return GatewayEvaluateResponse(
            valid=is_valid,
            reason=eval_result.get("reason"),
            request_id=eval_result.get("request_id"),
            purpose=eval_result.get("purpose"),
            claims=eval_result.get("claims", {}),
            generated_at=eval_result.get("generated_at"),
            proof=proof_schema,
        )
    except DisclosurePolicyError as err:
        return GatewayEvaluateResponse(
            valid=False,
            reason=str(err),
            request_id=request_id,
            purpose=req.purpose,
        )


# --- Phase 6: Cryptographic Proof Verification & Discovery ---

@app.post("/api/v1/proofs/verify", response_model=VerifyProofResponse)
def verify_proof_endpoint(payload: VerifyProofRequest) -> VerifyProofResponse:
    """Independent online verifier endpoint for validating Ed25519 signed proof envelopes."""
    proof_obj = Proof(
        proof_id=payload.proof.proof_id,
        issuer=payload.proof.issuer,
        audience=payload.proof.audience,
        issued_at=payload.proof.issued_at,
        expires_at=payload.proof.expires_at,
        nonce=payload.proof.nonce,
        claims=payload.proof.claims,
        key_id=payload.proof.key_id,
        signature=payload.proof.signature,
    )
    is_valid = verify_proof(
        proof_obj,
        public_key=GATEWAY_PUBLIC_KEY,
        expected_issuer=payload.expected_issuer,
        expected_audience=payload.expected_audience,
        expected_nonce=payload.expected_nonce,
    )
    if is_valid:
        return VerifyProofResponse(
            valid=True,
            status="TRUSTED_PROOF_VERIFIED",
            issuer=proof_obj.issuer,
            audience=proof_obj.audience,
            claims=proof_obj.claims,
            key_id=proof_obj.key_id,
        )
    return VerifyProofResponse(
        valid=False,
        status="INVALID_PROOF",
        reason="signature_mismatch_or_constraints_violated",
    )


@app.get("/api/v1/issuers/{issuer_id}/keys")
def get_issuer_keys_endpoint(issuer_id: str) -> dict[str, Any]:
    """Retrieve public keys for offline and independent verifier discovery."""
    return {
        "issuer": issuer_id,
        "keys": [
            {
                "kty": "OKP",
                "crv": "Ed25519",
                "kid": GATEWAY_KEY_ID,
                "x": _b64(GATEWAY_PUBLIC_KEY),
                "use": "sig",
                "alg": "EdDSA",
            }
        ],
    }





