import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.ids import generate_account_id
from app.db import Base


def uid() -> str:
    return str(uuid.uuid4())


def now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    digiin_account_id: Mapped[str] = mapped_column(String(40), unique=True, index=True, default=generate_account_id)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(32), default="CITIZEN")
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    def __init__(self, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = uid()
        if "digiin_account_id" not in kwargs:
            kwargs["digiin_account_id"] = generate_account_id()
        super().__init__(**kwargs)




class RefreshSession(Base):
    __tablename__ = "refresh_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(128))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(String(40))  # ISSUER, REQUESTER, GOVERNMENT
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE")


class Document(Base):
    __tablename__ = "user_documents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    document_type: Mapped[str] = mapped_column(String(100))
    source_type: Mapped[str] = mapped_column(String(32), default="SELF_UPLOAD")
    verification_status: Mapped[str] = mapped_column(String(32), default="UNVERIFIED")
    title: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class DocumentVersion(Base):
    __tablename__ = "user_document_versions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    document_id: Mapped[str] = mapped_column(ForeignKey("user_documents.id"), index=True)
    version: Mapped[int] = mapped_column(Integer)
    storage_key: Mapped[str] = mapped_column(Text)
    sha256: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Credential(Base):
    __tablename__ = "credentials"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    document_id: Mapped[str | None] = mapped_column(ForeignKey("user_documents.id"), nullable=True)
    credential_type: Mapped[str] = mapped_column(String(100))
    issuer_id: Mapped[str] = mapped_column(String(100))
    holder_name: Mapped[str] = mapped_column(String(200))
    passing_year: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="VERIFIED")
    verification_level: Mapped[int] = mapped_column(Integer, default=4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class VerificationRequest(Base):
    __tablename__ = "direct_verification_requests"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    requester_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    requester_name: Mapped[str] = mapped_column(String(200))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    credential_type: Mapped[str] = mapped_column(String(100))
    purpose: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="PENDING_CONSENT")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Consent(Base):
    __tablename__ = "consents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    request_id: Mapped[str] = mapped_column(ForeignKey("direct_verification_requests.id"), unique=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    decision: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class VerificationResult(Base):
    __tablename__ = "direct_verification_results"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    request_id: Mapped[str] = mapped_column(ForeignKey("direct_verification_requests.id"), unique=True)
    credential_id: Mapped[str | None] = mapped_column(ForeignKey("credentials.id"), nullable=True)
    result: Mapped[str] = mapped_column(String(32))
    verification_level: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class VerificationProof(Base):
    __tablename__ = "verification_proofs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    request_id: Mapped[str] = mapped_column(ForeignKey("direct_verification_requests.id"))
    proof_payload: Mapped[str] = mapped_column(Text)
    signature: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class CorrectionCase(Base):
    __tablename__ = "correction_cases"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    document_id: Mapped[str | None] = mapped_column(ForeignKey("user_documents.id"), nullable=True)
    issue_type: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="OPEN")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    actor_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100))
    resource_type: Mapped[str] = mapped_column(String(80))
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class DocumentJob(Base):
    __tablename__ = "document_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    document_id: Mapped[str] = mapped_column(ForeignKey("user_documents.id"), index=True)
    job_type: Mapped[str] = mapped_column(String(40))
    # State machine: QUEUED → RUNNING → SUCCEEDED / FAILED / RETRYING / CANCELLED
    status: Mapped[str] = mapped_column(String(32), default="QUEUED")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    priority: Mapped[int] = mapped_column(Integer, default=100)
    # available_at enables delayed/scheduled execution
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # worker_id for distributed concurrency (optimistic locking)
    worker_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(60), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class OCRAuditTrail(Base):
    """Immutable audit record of every OCR/extraction run — supports versioning and human-review fallback.

    Architecture rule: OCR/AI can extract evidence, but it can NEVER independently declare a
    government document authentic. Human (government officer) review is required when
    classification_confidence < 0.80 or requires_human_review is True.
    """

    __tablename__ = "ocr_audit_trail"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    document_id: Mapped[str] = mapped_column(ForeignKey("user_documents.id"), index=True)
    job_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    extraction_version: Mapped[int] = mapped_column(Integer, default=1)
    provider: Mapped[str] = mapped_column(String(60), default="LocalOCR")
    # Full OCR output snapshot (immutable after write)
    raw_extracted_json: Mapped[str] = mapped_column(Text, default="{}")
    # Structured fields after post-processing
    structured_fields_json: Mapped[str] = mapped_column(Text, default="{}")
    classification_type: Mapped[str] = mapped_column(String(60), default="OTHER")
    classification_confidence: Mapped[float] = mapped_column(default=0.0)
    # Human-review fallback trigger
    requires_human_review: Mapped[bool] = mapped_column(Boolean, default=False)
    human_review_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    human_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    human_reviewer_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    human_review_decision: Mapped[str | None] = mapped_column(String(40), nullable=True)  # APPROVED / REJECTED
    processing_duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class DocumentExtraction(Base):
    __tablename__ = "document_extractions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    document_id: Mapped[str] = mapped_column(ForeignKey("user_documents.id"), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    provider: Mapped[str] = mapped_column(String(60), default="LocalOCR")
    extracted_fields_json: Mapped[str] = mapped_column(Text, default="{}")
    classification_type: Mapped[str] = mapped_column(String(60), default="OTHER")
    classification_confidence: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class VerificationEvidence(Base):
    __tablename__ = "verification_evidence"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    document_id: Mapped[str] = mapped_column(ForeignKey("user_documents.id"), index=True)
    evidence_type: Mapped[str] = mapped_column(String(60))
    source: Mapped[str] = mapped_column(String(100))
    reference: Mapped[str] = mapped_column(String(150))
    result: Mapped[str] = mapped_column(String(40), default="MATCH")
    confidence: Mapped[float] = mapped_column(default=1.0)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    document_id: Mapped[str] = mapped_column(ForeignKey("user_documents.id"), index=True)
    score: Mapped[int] = mapped_column(Integer, default=100)
    level: Mapped[str] = mapped_column(String(32), default="LOW_RISK")
    factors_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class DocumentMatch(Base):
    __tablename__ = "document_matches"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    document_id: Mapped[str] = mapped_column(ForeignKey("user_documents.id"), index=True)
    matched_document_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    match_type: Mapped[str] = mapped_column(String(40), default="NO_MATCH")
    similarity_score: Mapped[float] = mapped_column(default=0.0)
    details_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class IntegrationEvent(Base):
    """Audit record for every external provider call — no PII or raw document bytes."""

    __tablename__ = "integration_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    event_id: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    provider_id: Mapped[str] = mapped_column(String(100), index=True)
    operation: Mapped[str] = mapped_column(String(80))
    request_id: Mapped[str] = mapped_column(String(80))
    correlation_id: Mapped[str] = mapped_column(String(80))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="STARTED")
    error_code: Mapped[str | None] = mapped_column(String(60), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")


class WebhookEvent(Base):
    """Persisted inbound webhook events (deduplicated by event_id)."""

    __tablename__ = "webhook_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    event_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    provider_id: Mapped[str] = mapped_column(String(100), index=True)
    event_type: Mapped[str] = mapped_column(String(80))
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)


class ProviderRegistration(Base):
    """Persisted provider manifests with trust metadata and lifecycle status."""

    __tablename__ = "provider_registrations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    provider_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    provider_type: Mapped[str] = mapped_column(String(40))
    issuer_id: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(200))
    version: Mapped[str] = mapped_column(String(20), default="v1")
    environment: Mapped[str] = mapped_column(String(20), default="development")
    capabilities_json: Mapped[str] = mapped_column(Text, default="[]")
    auth_method: Mapped[str] = mapped_column(String(40), default="none")
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE")
    trust_level: Mapped[str] = mapped_column(String(32), default="trusted")
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
