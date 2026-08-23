"""SQLAlchemy ORM models for persistent relational database storage."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

# --- Phase 3: Identity & Authentication Models ---

class DigiInAccountModel(Base):
    __tablename__ = "digiin_accounts"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(40), index=True)
    role: Mapped[str] = mapped_column(String(40), default="CITIZEN")
    status: Mapped[str] = mapped_column(String(40), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)


class IdentityClaimModel(Base):
    __tablename__ = "identity_claims"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(80), index=True)
    claim_type: Mapped[str] = mapped_column(String(80), index=True)
    value_reference: Mapped[str] = mapped_column(String(200))
    verification_level: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(140))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AuthChallengeModel(Base):
    __tablename__ = "auth_challenges"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(80), index=True)
    channel: Mapped[str] = mapped_column(String(40), default="SMS")
    challenge_hash: Mapped[str] = mapped_column(String(200))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class SessionModel(Base):
    __tablename__ = "sessions"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(80), index=True)
    token_family: Mapped[str] = mapped_column(String(80), index=True)
    refresh_token_hash: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class SecurityEventModel(Base):
    __tablename__ = "security_events"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(80), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    request_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")


# --- Phase 4: Credential Engine Models ---

class CredentialModel(Base):
    __tablename__ = "sovereign_credentials"
    __table_args__ = {"extend_existing": True}

    credential_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(80), index=True)
    credential_type: Mapped[str] = mapped_column(String(80), index=True)
    issuer: Mapped[str] = mapped_column(String(140))
    claims_json: Mapped[str] = mapped_column(Text, default="[]")
    issued_at: Mapped[datetime] = mapped_column(DateTime)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(40), index=True, default="active")
    verification_case_id: Mapped[str] = mapped_column(String(80), index=True)


# --- Phase 5: Verification Gateway Models ---

class GatewayVerificationRequestModel(Base):
    __tablename__ = "gateway_verification_requests"
    __table_args__ = {"extend_existing": True}

    request_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    verifier_id: Mapped[str] = mapped_column(String(80), index=True)
    account_id: Mapped[str] = mapped_column(String(80), index=True)
    purpose: Mapped[str] = mapped_column(String(200))
    requested_claim_types_json: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), index=True, default="pending")
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime)


class GatewayConsentModel(Base):
    __tablename__ = "gateway_consents"
    __table_args__ = {"extend_existing": True}

    consent_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    request_id: Mapped[str] = mapped_column(String(80), index=True, unique=True)
    account_id: Mapped[str] = mapped_column(String(80), index=True)
    decision: Mapped[str] = mapped_column(String(40))
    approved_claim_types_json: Mapped[str] = mapped_column(Text)
    granted_at: Mapped[datetime] = mapped_column(DateTime)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


# --- Phase 1 & 2: Documents, Versions, Jobs & Claims ---

class DocumentModel(Base):
    __tablename__ = "documents"

    document_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    owner_subject_id: Mapped[str] = mapped_column(String(80), index=True)
    owner_account_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    document_type: Mapped[str] = mapped_column(String(80))
    source: Mapped[str] = mapped_column(String(40))
    filename: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(40))
    authenticity: Mapped[str] = mapped_column(String(40))
    verification_level: Mapped[int] = mapped_column(Integer, default=0)
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    extracted_metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime)


class DocumentVersionModel(Base):
    __tablename__ = "document_versions"

    version_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(80), index=True)
    owner_account_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    parent_version_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    object_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    processing_status: Mapped[str | None] = mapped_column(String(40), default="completed")
    status: Mapped[str] = mapped_column(String(40))
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    change_summary: Mapped[str] = mapped_column(String(500))
    authority: Mapped[str] = mapped_column(String(140))
    evidence_reference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ProcessingJobModel(Base):
    __tablename__ = "processing_jobs"

    job_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(80), index=True)
    version_id: Mapped[str] = mapped_column(String(80), index=True)
    owner_account_id: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(40), default="queued")
    malware_scan_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    claims_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class DocumentClaimModel(Base):
    __tablename__ = "document_claims"

    claim_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(80), index=True)
    version_id: Mapped[str] = mapped_column(String(80), index=True)
    claim_key: Mapped[str] = mapped_column(String(80), index=True)
    claim_value: Mapped[str] = mapped_column(String(500))
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime)


class VerificationCaseModel(Base):
    __tablename__ = "verification_cases"

    case_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(80), index=True)
    claimed_issuer: Mapped[str] = mapped_column(String(140))
    status: Mapped[str] = mapped_column(String(40))
    automated_match_score: Mapped[int] = mapped_column(Integer, default=0)
    recommended_action: Mapped[str] = mapped_column(String(140))
    verifier_queue: Mapped[str] = mapped_column(String(80), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    decision_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class CorrectionRequestModel(Base):
    __tablename__ = "correction_requests"

    request_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(80), index=True)
    subject_id: Mapped[str] = mapped_column(String(80), default="subj_demo_5c7b90")
    field: Mapped[str] = mapped_column(String(80))
    current_value: Mapped[str] = mapped_column(String(200))
    proposed_value: Mapped[str] = mapped_column(String(200))
    reason: Mapped[str] = mapped_column(String(500))
    evidence_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    evidence_reference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(40))
    resulting_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reviewer_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    reviewer_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class WalletDocumentModel(Base):
    __tablename__ = "wallet_documents"

    document_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    subject_id: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(140))
    document_type: Mapped[str] = mapped_column(String(80))
    source: Mapped[str] = mapped_column(String(40))
    authenticity: Mapped[str] = mapped_column(String(40))
    validity_status: Mapped[str] = mapped_column(String(40))
    verification_level: Mapped[int] = mapped_column(Integer, default=0)
    verification_method: Mapped[str] = mapped_column(String(140))
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    issuer: Mapped[str] = mapped_column(String(140))
    valid_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    extracted_metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime)


class VerificationRequestModel(Base):
    __tablename__ = "verification_requests"

    request_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(80))
    requester_name: Mapped[str] = mapped_column(String(140))
    purpose: Mapped[str] = mapped_column(String(140))
    audience: Mapped[str] = mapped_column(String(140))
    requirements_json: Mapped[str] = mapped_column(Text)
    disclosure_mode: Mapped[str] = mapped_column(String(40))
    ttl_minutes: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(40))
    consent_text: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    expires_at: Mapped[datetime] = mapped_column(DateTime)


class VerificationResultModel(Base):
    __tablename__ = "verification_results"

    verification_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    request_id: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(40))
    subject_id: Mapped[str] = mapped_column(String(80))
    audience: Mapped[str] = mapped_column(String(140))
    purpose: Mapped[str] = mapped_column(String(140))
    disclosure_level: Mapped[str] = mapped_column(String(40))
    results_json: Mapped[str] = mapped_column(Text)
    proof_json: Mapped[str] = mapped_column(Text)
    receipt_json: Mapped[str] = mapped_column(Text)
    issued_at: Mapped[datetime] = mapped_column(DateTime)
    expires_at: Mapped[datetime] = mapped_column(DateTime)


class DomainEventModel(Base):
    __tablename__ = "domain_events"

    event_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(80))
    aggregate_id: Mapped[str] = mapped_column(String(80), index=True)
    actor: Mapped[str] = mapped_column(String(80))
    message: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime)
