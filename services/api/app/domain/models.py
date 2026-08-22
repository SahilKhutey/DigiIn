"""Canonical, provider-neutral models for the DigiIn prototype."""

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class TransactionState(StrEnum):
    CREATED = "created"
    AUTHENTICATED = "authenticated"
    CONSENTED = "consented"
    ISSUER_LOOKUP = "issuer_lookup"
    FETCHING = "fetching"
    RECEIVED = "received"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


class FailureCode(StrEnum):
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    ISSUER_TIMEOUT = "ISSUER_TIMEOUT"
    CALLBACK_FAILED = "CALLBACK_FAILED"
    JOURNEY_COMPLETE = "JOURNEY_COMPLETE"


class DocumentOption(BaseModel):
    id: str
    label: str
    category: str
    trustLabel: Literal["Government issued", "User uploaded", "Pending verification"]


class IssuerHealth(BaseModel):
    issuerId: str
    issuerName: str
    status: Literal["healthy", "degraded", "unavailable"]
    latencyMs: int | None = Field(default=None, ge=0)
    lastCheckedAt: datetime


class TransactionStep(BaseModel):
    name: str
    status: Literal["complete", "attention", "blocked", "not_started"]
    message: str
    owner: str
    nextAction: str | None = None


class RecoveryAction(BaseModel):
    label: str
    type: Literal["retry_later", "correct_record", "return_to_requester", "official_fallback"]
    guidance: str


class TransactionDiagnosis(BaseModel):
    transactionId: str = Field(pattern=r"^[a-z0-9-]{8,64}$")
    documentLabel: str
    trustLabel: Literal["Government issued", "User uploaded", "Pending verification"]
    state: TransactionState
    overallStatus: Literal["resolved", "action_required", "unavailable"]
    issueCode: FailureCode
    issuerStatus: Literal["available", "unavailable", "not_checked"]
    summary: str
    steps: list[TransactionStep]
    recovery: RecoveryAction
    fallbackAvailable: bool
    supportReference: str


class ConsentPreview(BaseModel):
    requesterName: str
    purpose: str
    scopes: list[str]
    access: str
    retentionNotice: str


class ScenarioSummary(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9-]{3,64}$")
    title: str
    description: str


class VerificationStatus(StrEnum):
    VERIFIED = "VERIFIED"
    NOT_VERIFIED = "NOT_VERIFIED"
    PENDING = "PENDING"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    NOT_FOUND = "NOT_FOUND"
    ISSUER_UNAVAILABLE = "ISSUER_UNAVAILABLE"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    PARTIAL = "PARTIAL"


class DisclosureLevel(StrEnum):
    BOOLEAN = "BOOLEAN"
    ATTRIBUTE = "ATTRIBUTE"
    DOCUMENT = "DOCUMENT"


class DisclosureMode(StrEnum):
    MINIMUM = "MINIMUM"
    ATTRIBUTE = "ATTRIBUTE"
    DOCUMENT_REQUIRED = "DOCUMENT_REQUIRED"


class VerificationPredicate(BaseModel):
    attribute: str
    operator: Literal["EQ", "GTE", "LTE"]
    value: str | int | bool


class VerificationRequirement(BaseModel):
    credential: str
    required: bool = True
    minimumLevel: int = Field(default=3, ge=0, le=5)
    attributes: list[str] = Field(default_factory=list)
    jurisdiction: str | None = None
    predicate: VerificationPredicate | None = None


class VerificationDisclosure(BaseModel):
    mode: DisclosureMode = DisclosureMode.MINIMUM
    attributes: list[str] = Field(default_factory=list)
    documentAccessJustification: str | None = None


class VerificationRequestCreate(BaseModel):
    clientId: str = Field(min_length=3, max_length=80)
    requesterName: str = Field(min_length=2, max_length=140)
    purpose: str = Field(min_length=3, max_length=120)
    audience: str = Field(min_length=3, max_length=120)
    requirements: list[VerificationRequirement] = Field(min_length=1, max_length=10)
    disclosure: VerificationDisclosure = Field(default_factory=VerificationDisclosure)
    ttlMinutes: int = Field(default=30, ge=5, le=240)


class VerificationRequestRecord(VerificationRequestCreate):
    requestId: str
    status: Literal["PENDING_CONSENT", "AUTHORIZED", "DECLINED", "EXPIRED"]
    createdAt: datetime
    expiresAt: datetime
    consentText: str


class CredentialProofResult(BaseModel):
    credential: str
    verified: bool
    status: VerificationStatus
    issuer: str | None = None
    level: int = Field(ge=0, le=5)
    disclosedAttributes: dict[str, Any] = Field(default_factory=dict)
    message: str


class VerificationProof(BaseModel):
    type: Literal["signed_verification_token"] = "signed_verification_token"
    token: str
    algorithm: Literal["HS256"] = "HS256"


class VerificationReceipt(BaseModel):
    verificationId: str
    requesterName: str
    purpose: str
    status: VerificationStatus
    shared: list[str]
    documentShared: bool
    issuedAt: datetime
    expiresAt: datetime


class VerificationResult(BaseModel):
    verificationId: str
    requestId: str
    status: VerificationStatus
    subjectId: str
    audience: str
    purpose: str
    disclosureLevel: DisclosureLevel
    results: list[CredentialProofResult]
    proof: VerificationProof
    receipt: VerificationReceipt
    issuedAt: datetime
    expiresAt: datetime


class VerificationAuthorization(BaseModel):
    allow: bool = True
    subjectId: str = Field(default="subj_demo_5c7b90", min_length=6, max_length=80)


class ProofTokenIntrospectionRequest(BaseModel):
    token: str
    audience: str
    nonce: str | None = None


class ProofTokenIntrospection(BaseModel):
    active: bool
    status: Literal["TRUSTED_PROOF", "INVALID_PROOF", "EXPIRED", "AUDIENCE_MISMATCH"]
    verificationId: str | None = None
    subjectId: str | None = None
    audience: str | None = None
    purpose: str | None = None
    expiresAt: datetime | None = None
    claims: dict[str, Any] = Field(default_factory=dict)
    message: str


class FeatureFlag(BaseModel):
    key: str
    enabled: bool
    description: str


class DomainEvent(BaseModel):
    eventId: str
    type: str
    aggregateId: str
    actor: str
    message: str
    createdAt: datetime


class PlatformTransaction(BaseModel):
    transactionId: str
    actor: str
    purpose: str
    requestedCredentials: list[str]
    currentStage: str
    state: Literal["PENDING", "RUNNING", "COMPLETED", "FAILED"]
    createdAt: datetime
    completedAt: datetime | None = None
    failureReason: str | None = None


class UploadedDocument(BaseModel):
    documentId: str
    ownerSubjectId: str
    documentType: str
    source: Literal["CITIZEN_UPLOAD", "GOVERNMENT_ISSUED", "LEGACY_RECORD"]
    filename: str
    status: Literal["UPLOADED", "CLASSIFIED", "PENDING_VERIFICATION", "VERIFIED", "REJECTED"]
    authenticity: Literal["UNKNOWN", "VERIFIED", "REJECTED"]
    verificationLevel: int = Field(ge=0, le=5)
    extractedMetadata: dict[str, Any] = Field(default_factory=dict)
    createdAt: datetime


class DocumentUploadRequest(BaseModel):
    ownerSubjectId: str = Field(default="subj_demo_5c7b90", min_length=6, max_length=80)
    filename: str = Field(default="class-xii-marksheet.pdf", min_length=3, max_length=160)
    documentType: str = Field(default="CLASS_XII", min_length=3, max_length=80)
    source: Literal["CITIZEN_UPLOAD", "LEGACY_RECORD"] = "CITIZEN_UPLOAD"


class GovernmentReviewDecision(BaseModel):
    decision: Literal["VERIFY", "REJECT", "REQUEST_MORE_EVIDENCE", "TRANSFER", "MARK_DUPLICATE"]
    verifierId: str = Field(default="officer_mock_cbse_01", min_length=3, max_length=80)
    note: str = Field(default="Synthetic verifier decision for local platform demo.", max_length=500)


class VerificationCase(BaseModel):
    caseId: str
    documentId: str
    claimedIssuer: str
    status: Literal[
        "NEW",
        "OCR_COMPLETE",
        "ISSUER_MATCHED",
        "UNDER_REVIEW",
        "VERIFIED",
        "REJECTED",
        "NEEDS_EVIDENCE",
    ]
    automatedMatchScore: int = Field(ge=0, le=100)
    recommendedAction: str
    verifierQueue: str
    createdAt: datetime
    decidedAt: datetime | None = None
    decision: GovernmentReviewDecision | None = None


class PolicyRequirement(BaseModel):
    credential: str
    minimumLevel: int = Field(ge=0, le=5)
    attributes: list[str] = Field(default_factory=list)


class PolicyDefinition(BaseModel):
    policyId: str
    purpose: str
    requesterName: str
    disclosureMode: DisclosureMode
    requirements: list[PolicyRequirement]


class MockIntegrationState(BaseModel):
    integrationId: str
    name: str
    domain: str
    supportedCredentials: list[str]
    scenarios: list[str]
    status: Literal["healthy", "degraded", "unavailable"]


class PlatformSnapshot(BaseModel):
    featureFlags: list[FeatureFlag]
    policies: list[PolicyDefinition]
    mockIntegrations: list[MockIntegrationState]
    documents: list[UploadedDocument]
    verificationCases: list[VerificationCase]
    transactions: list[PlatformTransaction]
    events: list[DomainEvent]


class StudentDemoResult(BaseModel):
    document: UploadedDocument
    verificationCase: VerificationCase
    transaction: PlatformTransaction
    proofRequest: VerificationRequestRecord
    proofResult: VerificationResult
    events: list[DomainEvent]
