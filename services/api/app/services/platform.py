"""Runnable in-memory platform foundation for the DigiIn vertical slice."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.domain.models import (
    DisclosureMode,
    DocumentUploadRequest,
    DomainEvent,
    FeatureFlag,
    GovernmentReviewDecision,
    MockIntegrationState,
    PlatformSnapshot,
    PlatformTransaction,
    PolicyDefinition,
    PolicyRequirement,
    StudentDemoResult,
    UploadedDocument,
    VerificationAuthorization,
    VerificationCase,
    VerificationRequestCreate,
    VerificationRequirement,
)
from app.services.verification import authorize_verification_request, create_verification_request

DOCUMENTS: dict[str, UploadedDocument] = {}
CASES: dict[str, VerificationCase] = {}
TRANSACTIONS: dict[str, PlatformTransaction] = {}
EVENTS: list[DomainEvent] = []

FEATURE_FLAGS = [
    FeatureFlag(
        key="FEATURE_DOCUMENT_UPLOAD",
        enabled=True,
        description="Enables citizen-uploaded document metadata and verification cases.",
    ),
    FeatureFlag(
        key="FEATURE_LEGACY_VERIFICATION",
        enabled=True,
        description="Enables legacy record verification workflow simulation.",
    ),
    FeatureFlag(
        key="FEATURE_AI_DOCUMENT_CLASSIFICATION",
        enabled=False,
        description="Reserved for assisted OCR/classification; no AI authority decisions.",
    ),
    FeatureFlag(
        key="FEATURE_EXTERNAL_ISSUER_API",
        enabled=False,
        description="Real issuer APIs are disabled in the synthetic prototype.",
    ),
    FeatureFlag(
        key="FEATURE_VERIFICATION_PROOFS",
        enabled=True,
        description="Enables purpose-bound proof token generation and introspection.",
    ),
]

POLICIES = [
    PolicyDefinition(
        policyId="policy_exam_eligibility_v1",
        purpose="EXAM_APPLICATION",
        requesterName="Demo Examination Portal",
        disclosureMode=DisclosureMode.MINIMUM,
        requirements=[
            PolicyRequirement(
                credential="CLASS_XII",
                minimumLevel=3,
                attributes=["qualification", "passing_year"],
            ),
            PolicyRequirement(
                credential="DOMICILE",
                minimumLevel=3,
                attributes=["jurisdiction"],
            ),
            PolicyRequirement(credential="AGE_OVER_18", minimumLevel=4),
        ],
    )
]

MOCK_INTEGRATIONS = [
    MockIntegrationState(
        integrationId="mock-cbse",
        name="Mock CBSE",
        domain="education",
        supportedCredentials=["CLASS_XII", "CLASS_XII_QUALIFICATION"],
        scenarios=[
            "SUCCESS",
            "TIMEOUT",
            "NOT_FOUND",
            "IDENTITY_MISMATCH",
            "API_DOWN",
            "INVALID_RECORD",
            "REQUIRES_HUMAN_REVIEW",
        ],
        status="healthy",
    ),
    MockIntegrationState(
        integrationId="mock-university",
        name="Mock State University",
        domain="university",
        supportedCredentials=["GRADUATION"],
        scenarios=["SUCCESS", "TIMEOUT", "NOT_FOUND", "REQUIRES_HUMAN_REVIEW"],
        status="degraded",
    ),
    MockIntegrationState(
        integrationId="mock-legacy-archive",
        name="Mock Legacy Archive",
        domain="legacy",
        supportedCredentials=["LEGACY_CERTIFICATE", "LAND_RECORD"],
        scenarios=["SUCCESS", "NOT_FOUND", "REQUIRES_HUMAN_REVIEW"],
        status="healthy",
    ),
]


def platform_snapshot() -> PlatformSnapshot:
    return PlatformSnapshot(
        featureFlags=FEATURE_FLAGS,
        policies=POLICIES,
        mockIntegrations=MOCK_INTEGRATIONS,
        documents=list(DOCUMENTS.values()),
        verificationCases=list(CASES.values()),
        transactions=list(TRANSACTIONS.values()),
        events=EVENTS[-50:],
    )


def upload_document(payload: DocumentUploadRequest) -> UploadedDocument:
    now = datetime.now(UTC)
    document = UploadedDocument(
        documentId=f"doc_{uuid4().hex[:12]}",
        ownerSubjectId=payload.ownerSubjectId,
        documentType=payload.documentType,
        source=payload.source,
        filename=payload.filename,
        status="UPLOADED",
        authenticity="UNKNOWN",
        verificationLevel=0,
        extractedMetadata={},
        createdAt=now,
    )
    DOCUMENTS[document.documentId] = document
    _event("DocumentUploaded", document.documentId, payload.ownerSubjectId, "Document metadata accepted.")
    return document


def classify_document(document_id: str) -> UploadedDocument | None:
    document = DOCUMENTS.get(document_id)
    if document is None:
        return None
    metadata = {
        "qualification": "Class XII" if document.documentType == "CLASS_XII" else document.documentType,
        "passing_year": 2026,
        "detected_issuer": _claimed_issuer(document.documentType),
        "classification_confidence": 92,
    }
    updated = document.model_copy(
        update={
            "status": "CLASSIFIED",
            "verificationLevel": 1,
            "extractedMetadata": metadata,
        }
    )
    DOCUMENTS[document_id] = updated
    _event("DocumentClassified", document_id, document.ownerSubjectId, "OCR and metadata extraction completed.")
    return updated


def create_verification_case(document_id: str) -> VerificationCase | None:
    document = DOCUMENTS.get(document_id)
    if document is None:
        return None
    if document.status == "UPLOADED":
        document = classify_document(document_id)
        if document is None:
            return None
    case = VerificationCase(
        caseId=f"case_{uuid4().hex[:12]}",
        documentId=document.documentId,
        claimedIssuer=_claimed_issuer(document.documentType),
        status="UNDER_REVIEW",
        automatedMatchScore=88,
        recommendedAction="Manual verification recommended after issuer match.",
        verifierQueue="mock-cbse-verifier-queue",
        createdAt=datetime.now(UTC),
    )
    CASES[case.caseId] = case
    updated_doc = document.model_copy(update={"status": "PENDING_VERIFICATION", "verificationLevel": 2})
    DOCUMENTS[document.documentId] = updated_doc
    _event("VerificationCaseCreated", case.caseId, document.ownerSubjectId, "Case routed to government verifier queue.")
    return case


def decide_verification_case(
    case_id: str, decision: GovernmentReviewDecision
) -> VerificationCase | None:
    case = CASES.get(case_id)
    if case is None:
        return None
    document = DOCUMENTS[case.documentId]
    verified = decision.decision == "VERIFY"
    updated_case = case.model_copy(
        update={
            "status": "VERIFIED" if verified else "REJECTED",
            "decidedAt": datetime.now(UTC),
            "decision": decision,
        }
    )
    CASES[case_id] = updated_case
    DOCUMENTS[document.documentId] = document.model_copy(
        update={
            "status": "VERIFIED" if verified else "REJECTED",
            "authenticity": "VERIFIED" if verified else "REJECTED",
            "verificationLevel": 4 if verified else document.verificationLevel,
        }
    )
    _event(
        "VerificationCompleted" if verified else "VerificationRejected",
        case.caseId,
        decision.verifierId,
        f"Government verifier decision: {decision.decision}.",
    )
    return updated_case


def run_student_demo() -> StudentDemoResult:
    document = upload_document(
        DocumentUploadRequest(
            filename="student-class-xii-marksheet.pdf",
            documentType="CLASS_XII",
            source="CITIZEN_UPLOAD",
        )
    )
    classified = classify_document(document.documentId)
    if classified is None:
        raise RuntimeError("Failed to classify synthetic document.")
    case = create_verification_case(classified.documentId)
    if case is None:
        raise RuntimeError("Failed to create synthetic verification case.")
    decision = GovernmentReviewDecision(decision="VERIFY", note="Mock CBSE record matched.")
    decided_case = decide_verification_case(case.caseId, decision)
    if decided_case is None:
        raise RuntimeError("Failed to decide synthetic verification case.")
    transaction = _transaction(
        actor=classified.ownerSubjectId,
        purpose="EXAM_APPLICATION",
        requested_credentials=["CLASS_XII", "DOMICILE", "AGE_OVER_18"],
        current_stage="Signed proof generated",
        state="COMPLETED",
    )
    proof_request = create_verification_request(_exam_policy_request())
    proof_result = authorize_verification_request(
        proof_request.requestId, VerificationAuthorization(allow=True, subjectId=classified.ownerSubjectId)
    )
    if proof_result is None:
        raise RuntimeError("Failed to generate synthetic proof.")
    _event(
        "ProofGenerated",
        proof_result.verificationId,
        classified.ownerSubjectId,
        "Purpose-bound eligibility proof generated for requester.",
    )
    return StudentDemoResult(
        document=DOCUMENTS[classified.documentId],
        verificationCase=decided_case,
        transaction=transaction,
        proofRequest=proof_request,
        proofResult=proof_result,
        events=EVENTS[-10:],
    )


def _exam_policy_request() -> VerificationRequestCreate:
    policy = POLICIES[0]
    return VerificationRequestCreate(
        clientId="nta-2026",
        requesterName=policy.requesterName,
        purpose=policy.purpose,
        audience="NTA_APPLICATION_PORTAL",
        disclosure={"mode": policy.disclosureMode},
        requirements=[
            VerificationRequirement(
                credential=item.credential,
                minimumLevel=item.minimumLevel,
                attributes=item.attributes,
            )
            for item in policy.requirements
        ],
    )


def _transaction(
    actor: str,
    purpose: str,
    requested_credentials: list[str],
    current_stage: str,
    state: str,
) -> PlatformTransaction:
    now = datetime.now(UTC)
    transaction = PlatformTransaction(
        transactionId=f"tx_{uuid4().hex[:12]}",
        actor=actor,
        purpose=purpose,
        requestedCredentials=requested_credentials,
        currentStage=current_stage,
        state=state,  # type: ignore[arg-type]
        createdAt=now,
        completedAt=now if state == "COMPLETED" else None,
    )
    TRANSACTIONS[transaction.transactionId] = transaction
    _event("TransactionCompleted", transaction.transactionId, actor, current_stage)
    return transaction


def _claimed_issuer(document_type: str) -> str:
    if document_type == "CLASS_XII":
        return "Mock CBSE"
    if document_type == "GRADUATION":
        return "Mock State University"
    return "Mock Legacy Archive"


def _event(event_type: str, aggregate_id: str, actor: str, message: str) -> DomainEvent:
    event = DomainEvent(
        eventId=f"evt_{uuid4().hex[:12]}",
        type=event_type,
        aggregateId=aggregate_id,
        actor=actor,
        message=message,
        createdAt=datetime.now(UTC),
    )
    EVENTS.append(event)
    return event
