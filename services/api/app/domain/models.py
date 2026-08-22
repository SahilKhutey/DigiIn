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
    operator: Literal["EQ", "GTE", "LTE", "IN", "EXISTS"]
    value: Any = None
    label: str | None = None


class PredicateProofResult(BaseModel):
    predicateId: str
    claimName: str
    expression: str
    satisfied: bool
    proofType: Literal["DERIVED_ZERO_KNOWLEDGE_PREDICATE"] = "DERIVED_ZERO_KNOWLEDGE_PREDICATE"
    maskedAttributes: list[str] = Field(default_factory=list)


class SelectiveDisclosurePreference(BaseModel):
    mode: Literal["PREDICATE_ONLY", "SELECTIVE_ATTRIBUTES", "FULL_DOCUMENT"] = "PREDICATE_ONLY"
    selectedAttributes: list[str] = Field(default_factory=list)
    selectedPredicates: list[str] = Field(default_factory=list)


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
    predicateResults: list[PredicateProofResult] = Field(default_factory=list)
    maskedAttributes: list[str] = Field(default_factory=list)
    message: str


class VerificationProof(BaseModel):
    type: Literal["signed_verification_token"] = "signed_verification_token"
    token: str
    algorithm: Literal["EdDSA", "RS256", "HS256"] = "EdDSA"
    keyId: str | None = None


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
    predicateProofs: list[PredicateProofResult] = Field(default_factory=list)
    maskedAttributesSummary: list[str] = Field(default_factory=list)
    proof: VerificationProof
    receipt: VerificationReceipt
    issuedAt: datetime
    expiresAt: datetime


class VerificationAuthorization(BaseModel):
    allow: bool = True
    subjectId: str = Field(default="subj_demo_5c7b90", min_length=6, max_length=80)
    customDisclosure: SelectiveDisclosurePreference | None = None


class ConsentRecord(BaseModel):
    consentId: str
    verificationId: str
    requestId: str
    subjectId: str
    requesterName: str
    clientId: str
    purpose: str
    audience: str
    disclosureLevel: DisclosureLevel
    credentialsVerified: list[str]
    predicateCount: int
    maskedAttributesCount: int
    status: Literal["ACTIVE", "REVOKED", "EXPIRED"]
    issuedAt: datetime
    expiresAt: datetime
    revokedAt: datetime | None = None
    revocationReason: str | None = None


class RevokeConsentPayload(BaseModel):
    reason: str = Field(default="Citizen requested credential revocation.", max_length=200)




class ProofTokenIntrospectionRequest(BaseModel):
    token: str
    audience: str
    nonce: str | None = None


class JwkKey(BaseModel):
    kty: str
    kid: str
    use: str = "sig"
    alg: str
    crv: str | None = None
    x: str | None = None
    n: str | None = None
    e: str | None = None


class JwksResponse(BaseModel):
    keys: list[JwkKey]


class ProofTokenIntrospection(BaseModel):
    active: bool
    status: Literal["TRUSTED_PROOF", "INVALID_PROOF", "EXPIRED", "AUDIENCE_MISMATCH", "REVOKED"]
    verificationId: str | None = None
    subjectId: str | None = None

    audience: str | None = None
    purpose: str | None = None
    expiresAt: datetime | None = None
    claims: dict[str, Any] = Field(default_factory=dict)
    keyId: str | None = None
    algorithm: str | None = None
    cryptoVerified: bool = True
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


class DocumentVersionStatus(StrEnum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"
    REVOKED = "REVOKED"


class DocumentVersionRecord(BaseModel):
    versionId: str
    versionNumber: int = Field(ge=1)
    documentId: str
    parentVersionId: str | None = None
    status: DocumentVersionStatus = DocumentVersionStatus.ACTIVE
    metadata: dict[str, Any] = Field(default_factory=dict)
    changeSummary: str
    authority: str
    evidenceReference: str | None = None
    createdAt: datetime
    supersededAt: datetime | None = None


class CorrectionStatus(StrEnum):
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MORE_INFO_REQUIRED = "MORE_INFO_REQUIRED"


class CorrectionDecisionType(StrEnum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_EVIDENCE = "REQUEST_EVIDENCE"


class CorrectionRequestCreate(BaseModel):
    field: str = Field(min_length=1, max_length=80)
    currentValue: str = Field(min_length=1, max_length=200)
    proposedValue: str = Field(min_length=1, max_length=200)
    reason: str = Field(min_length=3, max_length=500)
    evidenceDescription: str | None = Field(default=None, max_length=500)
    evidenceReference: str | None = Field(default=None, max_length=100)


class CorrectionReviewDecision(BaseModel):
    decision: CorrectionDecisionType
    reviewerId: str = Field(default="officer_mock_cbse_01", min_length=3, max_length=80)
    note: str = Field(default="Reviewed and verified against secondary official records.", max_length=500)
    correctedFields: dict[str, Any] = Field(default_factory=dict)


class CorrectionRequestRecord(BaseModel):
    requestId: str
    documentId: str
    subjectId: str
    field: str
    currentValue: str
    proposedValue: str
    reason: str
    evidenceDescription: str | None = None
    evidenceReference: str | None = None
    status: CorrectionStatus
    resultingVersion: int | None = None
    reviewerId: str | None = None
    reviewerNote: str | None = None
    createdAt: datetime
    decidedAt: datetime | None = None


class DocumentSource(StrEnum):
    GOVERNMENT_ISSUED = "GOVERNMENT_ISSUED"
    CITIZEN_UPLOAD = "CITIZEN_UPLOAD"
    LEGACY_RECORD = "LEGACY_RECORD"


class AuthenticityStatus(StrEnum):
    VERIFIED = "VERIFIED"
    UNKNOWN = "UNKNOWN"
    REJECTED = "REJECTED"


class ValidityStatus(StrEnum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    SUPERSEDED = "SUPERSEDED"


class WalletDocument(BaseModel):
    documentId: str
    title: str
    documentType: str
    source: DocumentSource
    authenticity: AuthenticityStatus
    validityStatus: ValidityStatus
    verificationLevel: int = Field(ge=0, le=5)
    verificationMethod: str
    currentVersion: int = Field(default=1, ge=1)
    issuer: str
    validUntil: datetime | None = None
    extractedMetadata: dict[str, Any] = Field(default_factory=dict)
    createdAt: datetime


class UploadedDocument(BaseModel):
    documentId: str
    ownerSubjectId: str
    documentType: str
    source: Literal["CITIZEN_UPLOAD", "GOVERNMENT_ISSUED", "LEGACY_RECORD"]
    filename: str
    status: Literal["UPLOADED", "CLASSIFIED", "PENDING_VERIFICATION", "VERIFIED", "REJECTED"]
    authenticity: Literal["UNKNOWN", "VERIFIED", "REJECTED"]
    verificationLevel: int = Field(ge=0, le=5)
    currentVersion: int = Field(default=1, ge=1)
    extractedMetadata: dict[str, Any] = Field(default_factory=dict)
    createdAt: datetime



class DocumentUploadRequest(BaseModel):
    ownerSubjectId: str = Field(default="subj_demo_5c7b90", min_length=6, max_length=80)
    filename: str = Field(default="class-xii-marksheet.pdf", min_length=3, max_length=160)
    documentType: str = Field(default="CLASS_XII", min_length=3, max_length=80)
    source: Literal["CITIZEN_UPLOAD", "LEGACY_RECORD"] = "CITIZEN_UPLOAD"


class DirectUploadPayload(BaseModel):
    ownerSubjectId: str = Field(default="subj_demo_5c7b90", min_length=6, max_length=80)
    filename: str = Field(default="uploaded_document.pdf", min_length=3, max_length=160)
    documentTypeHint: str | None = None
    simulatedContent: str | None = None


class DocumentClassificationResult(BaseModel):
    documentId: str
    documentType: str
    confidenceScore: int = Field(ge=0, le=100)
    extractedFields: dict[str, Any] = Field(default_factory=dict)
    detectedIssuer: str
    suggestedQueue: str
    classificationNotes: list[str] = Field(default_factory=list)
    sha256: str
    fileSizeKb: int = 150


class VerifierQueueId(StrEnum):

    QUEUE_CBSE = "queue_cbse"
    QUEUE_REVENUE = "queue_revenue"
    QUEUE_TRANSPORT = "queue_transport"
    QUEUE_GENERAL = "queue_general"


class VerifierQueueSummary(BaseModel):
    queueId: VerifierQueueId
    name: str
    department: str
    pendingCount: int = 0
    verifiedCount: int = 0
    totalCount: int = 0


class FieldComparison(BaseModel):
    field: str
    label: str
    citizenValue: str
    registryValue: str
    isMatch: bool
    matchConfidence: int = Field(ge=0, le=100)
    discrepancyNote: str | None = None


class EvidenceComparisonDetail(BaseModel):
    caseId: str
    documentId: str
    documentType: str
    subjectId: str
    verifierQueue: VerifierQueueId
    claimedIssuer: str
    overallMatchScore: int = Field(ge=0, le=100)
    recommendedAction: str
    citizenClaims: dict[str, Any] = Field(default_factory=dict)
    officialRegistryClaims: dict[str, Any] = Field(default_factory=dict)
    fieldComparisons: list[FieldComparison] = Field(default_factory=list)
    caseStatus: str
    createdAt: datetime


class GovernmentReviewDecision(BaseModel):
    decision: Literal["VERIFY", "REJECT", "REQUEST_MORE_EVIDENCE", "TRANSFER", "MARK_DUPLICATE"]
    verifierId: str = Field(default="officer_mock_cbse_01", min_length=3, max_length=80)
    note: str = Field(default="Synthetic verifier decision for local platform demo.", max_length=500)
    transferQueue: VerifierQueueId | None = None


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
    verifierQueue: VerifierQueueId = VerifierQueueId.QUEUE_CBSE
    createdAt: datetime
    decidedAt: datetime | None = None
    decision: GovernmentReviewDecision | None = None


class PipelineUploadResponse(BaseModel):
    document: UploadedDocument
    classification: DocumentClassificationResult
    verificationCase: VerificationCase
    walletDocument: WalletDocument
    message: str




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
    versions: list[DocumentVersionRecord] = Field(default_factory=list)
    verificationCases: list[VerificationCase]
    corrections: list[CorrectionRequestRecord] = Field(default_factory=list)
    transactions: list[PlatformTransaction]
    events: list[DomainEvent]


class StudentDemoResult(BaseModel):
    document: UploadedDocument
    verificationCase: VerificationCase
    transaction: PlatformTransaction
    proofRequest: VerificationRequestRecord
    proofResult: VerificationResult
    events: list[DomainEvent]


class SupportSafeSummary(BaseModel):
    supportCode: str
    timestamp: datetime
    scenarioId: str
    failureStage: str
    diagnosticTitle: str
    plainLanguageExplanation: str
    affectedAuthority: str
    issuerStatus: str
    correlationId: str
    guidanceForCitizen: list[str] = Field(default_factory=list)
    guidanceForDeskOfficer: list[str] = Field(default_factory=list)
    securityNotice: str
    qrDigest: str


class EkycOtpRequest(BaseModel):
    aadhaarRef: str
    purpose: str = "Citizen Identity Verification"


class EkycOtpResponse(BaseModel):
    txnId: str
    maskedMobile: str
    expiresInSeconds: int = 600
    demoOtpHint: str
    message: str


class EkycVerifyRequest(BaseModel):
    txnId: str
    otp: str
    documentId: str | None = None


class EkycIdentitySnapshot(BaseModel):
    name: str
    dob: str
    gender: str
    maskedAadhaar: str
    state: str
    district: str
    pincode: str


class EkycMatchResult(BaseModel):
    nameMatch: bool
    dobMatch: bool
    stateMatch: bool
    score: int
    verdict: Literal["EXACT_MATCH", "HIGH_CONFIDENCE_MATCH", "PARTIAL_MATCH", "MISMATCH"]
    claimedValues: dict[str, str] = Field(default_factory=dict)
    officialValues: dict[str, str] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class EkycVerifyResponse(BaseModel):
    txnId: str
    status: Literal["VERIFIED", "FAILED", "EXPIRED"]
    identitySnapshot: EkycIdentitySnapshot
    matchResult: EkycMatchResult
    elevatedDocumentLevel: int | None = None
    ekycProofToken: str
    keyId: str
    algorithm: Literal["EdDSA"] = "EdDSA"
    verifiedAt: datetime
    message: str


class EkycMatchDemographicsRequest(BaseModel):
    claimedName: str
    claimedDob: str | None = None
    claimedState: str | None = None
    aadhaarRef: str



