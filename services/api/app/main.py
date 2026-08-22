"""DigiIn modular-monolith API entry point."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.domain.models import (
    ConsentPreview,
    DocumentUploadRequest,
    DocumentOption,
    GovernmentReviewDecision,
    IssuerHealth,
    PlatformSnapshot,
    ProofTokenIntrospection,
    ProofTokenIntrospectionRequest,
    ScenarioSummary,
    StudentDemoResult,
    TransactionDiagnosis,
    UploadedDocument,
    VerificationAuthorization,
    VerificationCase,
    VerificationRequestCreate,
    VerificationRequestRecord,
    VerificationResult,
)
from app.services.platform import (
    classify_document,
    create_verification_case,
    decide_verification_case,
    platform_snapshot,
    run_student_demo,
    upload_document,
)
from app.services.catalogue import get_document, search_documents
from app.services.recovery import get_diagnosis, list_scenarios
from app.services.trust import consent_preview, issuer_health
from app.services.verification import (
    authorize_verification_request,
    create_verification_request,
    demo_exam_request,
    get_verification_request,
    get_verification_result,
    introspect_token,
    list_verification_requests,
    result_for_request,
)

app = FastAPI(title="DigiIn Prototype API", version="0.4.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "digiin-api", "mode": "synthetic-prototype"}


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


@app.get("/api/v1/scenarios", response_model=list[ScenarioSummary])
def scenarios() -> list[ScenarioSummary]:
    return list_scenarios()


@app.get("/api/v1/transactions/{transaction_id}/diagnosis", response_model=TransactionDiagnosis)
def transaction_diagnosis(transaction_id: str) -> TransactionDiagnosis:
    diagnosis = get_diagnosis(transaction_id)
    if diagnosis is None:
        raise HTTPException(status_code=404, detail="Transaction diagnosis not found")
    return diagnosis


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


@app.get("/api/v1/platform/snapshot", response_model=PlatformSnapshot)
def read_platform_snapshot() -> PlatformSnapshot:
    """Read the current synthetic platform state: flags, policies, integrations and events."""
    return platform_snapshot()


@app.post("/api/v1/documents/upload", response_model=UploadedDocument)
def create_uploaded_document(payload: DocumentUploadRequest) -> UploadedDocument:
    """Create citizen-uploaded document metadata; no real file is accepted in the prototype."""
    return upload_document(payload)


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


@app.post("/api/v1/platform/demo/student", response_model=StudentDemoResult)
def run_student_vertical_slice() -> StudentDemoResult:
    """Run the canonical student upload -> government verification -> requester proof demo."""
    return run_student_demo()
