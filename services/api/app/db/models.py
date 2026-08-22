"""SQLAlchemy ORM models for persistent relational database storage."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class DocumentModel(Base):
    __tablename__ = "documents"

    document_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    owner_subject_id: Mapped[str] = mapped_column(String(80), index=True)
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
    version_number: Mapped[int] = mapped_column(Integer)
    parent_version_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(40))
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    change_summary: Mapped[str] = mapped_column(String(500))
    authority: Mapped[str] = mapped_column(String(140))
    evidence_reference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


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
