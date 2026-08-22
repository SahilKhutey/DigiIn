"""Database repository layer providing CRUD operations and seed data management."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models import (
    CorrectionRequestModel,
    DocumentModel,
    DocumentVersionModel,
    DomainEventModel,
    VerificationCaseModel,
    VerificationRequestModel,
    VerificationResultModel,
    WalletDocumentModel,
)
from app.db.session import get_db_session
from app.domain.models import (
    CorrectionRequestRecord,
    CorrectionReviewDecision,
    CorrectionStatus,
    DocumentVersionRecord,
    DocumentVersionStatus,
    DomainEvent,
    GovernmentReviewDecision,
    UploadedDocument,
    VerificationCase,
    VerificationRequestCreate,
    VerificationRequestRecord,
    VerificationResult,
    VerifierQueueId,
    WalletDocument,
)


# --- Document Repository ---

def save_document(doc: UploadedDocument, session: Session | None = None) -> UploadedDocument:
    def _op(s: Session) -> UploadedDocument:
        db_doc = s.get(DocumentModel, doc.documentId)
        if db_doc is None:
            db_doc = DocumentModel(
                document_id=doc.documentId,
                owner_subject_id=doc.ownerSubjectId,
                document_type=doc.documentType,
                source=doc.source,
                filename=doc.filename,
                status=doc.status,
                authenticity=doc.authenticity,
                verification_level=doc.verificationLevel,
                current_version=doc.currentVersion,
                extracted_metadata_json=json.dumps(doc.extractedMetadata),
                created_at=doc.createdAt,
            )
            s.add(db_doc)
        else:
            db_doc.status = doc.status
            db_doc.authenticity = doc.authenticity
            db_doc.verification_level = doc.verificationLevel
            db_doc.current_version = doc.currentVersion
            db_doc.extracted_metadata_json = json.dumps(doc.extractedMetadata)
        return doc

    if session:
        return _op(session)
    with get_db_session() as s:
        return _op(s)


def get_document(document_id: str) -> UploadedDocument | None:
    with get_db_session() as s:
        row = s.get(DocumentModel, document_id)
        if row is None:
            return None
        return UploadedDocument(
            documentId=row.document_id,
            ownerSubjectId=row.owner_subject_id,
            documentType=row.document_type,
            source=row.source,  # type: ignore[arg-type]
            filename=row.filename,
            status=row.status,  # type: ignore[arg-type]
            authenticity=row.authenticity,  # type: ignore[arg-type]
            verificationLevel=row.verification_level,
            currentVersion=row.current_version,
            extractedMetadata=json.loads(row.extracted_metadata_json),
            createdAt=row.created_at,
        )


def list_documents() -> list[UploadedDocument]:
    with get_db_session() as s:
        stmt = select(DocumentModel).order_by(desc(DocumentModel.created_at))
        rows = s.scalars(stmt).all()
        return [
            UploadedDocument(
                documentId=r.document_id,
                ownerSubjectId=r.owner_subject_id,
                documentType=r.document_type,
                source=r.source,  # type: ignore[arg-type]
                filename=r.filename,
                status=r.status,  # type: ignore[arg-type]
                authenticity=r.authenticity,  # type: ignore[arg-type]
                verificationLevel=r.verification_level,
                currentVersion=r.current_version,
                extractedMetadata=json.loads(r.extracted_metadata_json),
                createdAt=r.created_at,
            )
            for r in rows
        ]


# --- Document Versions ---

def save_document_version(v: DocumentVersionRecord, session: Session | None = None) -> DocumentVersionRecord:
    def _op(s: Session) -> DocumentVersionRecord:
        db_v = s.get(DocumentVersionModel, v.versionId)
        if db_v is None:
            db_v = DocumentVersionModel(
                version_id=v.versionId,
                document_id=v.documentId,
                version_number=v.versionNumber,
                parent_version_id=v.parentVersionId,
                status=v.status,
                metadata_json=json.dumps(v.metadata),
                change_summary=v.changeSummary,
                authority=v.authority,
                evidence_reference=v.evidenceReference,
                created_at=v.createdAt,
                superseded_at=v.supersededAt,
            )
            s.add(db_v)
        else:
            db_v.status = v.status
            db_v.superseded_at = v.supersededAt
        return v

    if session:
        return _op(session)
    with get_db_session() as s:
        return _op(s)


def get_document_versions(document_id: str) -> list[DocumentVersionRecord]:
    with get_db_session() as s:
        stmt = (
            select(DocumentVersionModel)
            .where(DocumentVersionModel.document_id == document_id)
            .order_by(DocumentVersionModel.version_number)
        )
        rows = s.scalars(stmt).all()
        return [
            DocumentVersionRecord(
                versionId=r.version_id,
                documentId=r.document_id,
                versionNumber=r.version_number,
                parentVersionId=r.parent_version_id,
                status=DocumentVersionStatus(r.status),
                metadata=json.loads(r.metadata_json),
                changeSummary=r.change_summary,
                authority=r.authority,
                evidenceReference=r.evidence_reference,
                createdAt=r.created_at,
                supersededAt=r.superseded_at,
            )
            for r in rows
        ]


def list_all_versions() -> list[DocumentVersionRecord]:
    with get_db_session() as s:
        stmt = select(DocumentVersionModel).order_by(desc(DocumentVersionModel.created_at))
        rows = s.scalars(stmt).all()
        return [
            DocumentVersionRecord(
                versionId=r.version_id,
                documentId=r.document_id,
                versionNumber=r.version_number,
                parentVersionId=r.parent_version_id,
                status=DocumentVersionStatus(r.status),
                metadata=json.loads(r.metadata_json),
                changeSummary=r.change_summary,
                authority=r.authority,
                evidenceReference=r.evidence_reference,
                createdAt=r.created_at,
                supersededAt=r.superseded_at,
            )
            for r in rows
        ]


# --- Verification Cases ---

def save_verification_case(case: VerificationCase, session: Session | None = None) -> VerificationCase:
    def _op(s: Session) -> VerificationCase:
        db_c = s.get(VerificationCaseModel, case.caseId)
        decision_data = case.decision.model_dump() if case.decision else None
        if db_c is None:
            db_c = VerificationCaseModel(
                case_id=case.caseId,
                document_id=case.documentId,
                claimed_issuer=case.claimedIssuer,
                status=case.status,
                automated_match_score=case.automatedMatchScore,
                recommended_action=case.recommendedAction,
                verifier_queue=case.verifierQueue.value if hasattr(case.verifierQueue, "value") else str(case.verifierQueue),
                created_at=case.createdAt,
                decided_at=case.decidedAt,
                decision_json=json.dumps(decision_data) if decision_data else None,
            )
            s.add(db_c)
        else:
            db_c.status = case.status
            db_c.verifier_queue = case.verifierQueue.value if hasattr(case.verifierQueue, "value") else str(case.verifierQueue)
            db_c.decided_at = case.decidedAt
            db_c.decision_json = json.dumps(decision_data) if decision_data else None
        return case

    if session:
        return _op(session)
    with get_db_session() as s:
        return _op(s)


def get_verification_case(case_id: str) -> VerificationCase | None:
    with get_db_session() as s:
        r = s.get(VerificationCaseModel, case_id)
        if r is None:
            return None
        dec = json.loads(r.decision_json) if r.decision_json else None
        return VerificationCase(
            caseId=r.case_id,
            documentId=r.document_id,
            claimedIssuer=r.claimed_issuer,
            status=r.status,  # type: ignore[arg-type]
            automatedMatchScore=r.automated_match_score,
            recommendedAction=r.recommended_action,
            verifierQueue=VerifierQueueId(r.verifier_queue),
            createdAt=r.created_at,
            decidedAt=r.decided_at,
            decision=GovernmentReviewDecision(**dec) if dec else None,
        )


def list_verification_cases(queue_id: str | None = None, status: str | None = None) -> list[VerificationCase]:
    with get_db_session() as s:
        stmt = select(VerificationCaseModel)
        if queue_id:
            stmt = stmt.where(VerificationCaseModel.verifier_queue == queue_id)
        if status:
            stmt = stmt.where(VerificationCaseModel.status == status)
        stmt = stmt.order_by(desc(VerificationCaseModel.created_at))
        rows = s.scalars(stmt).all()
        res: list[VerificationCase] = []
        for r in rows:
            dec = json.loads(r.decision_json) if r.decision_json else None
            res.append(
                VerificationCase(
                    caseId=r.case_id,
                    documentId=r.document_id,
                    claimedIssuer=r.claimed_issuer,
                    status=r.status,  # type: ignore[arg-type]
                    automatedMatchScore=r.automated_match_score,
                    recommendedAction=r.recommended_action,
                    verifierQueue=VerifierQueueId(r.verifier_queue),
                    createdAt=r.created_at,
                    decidedAt=r.decided_at,
                    decision=GovernmentReviewDecision(**dec) if dec else None,
                )
            )
        return res


# --- Correction Requests ---

def save_correction(req: CorrectionRequestRecord, session: Session | None = None) -> CorrectionRequestRecord:
    def _op(s: Session) -> CorrectionRequestRecord:
        db_c = s.get(CorrectionRequestModel, req.requestId)
        if db_c is None:
            db_c = CorrectionRequestModel(
                request_id=req.requestId,
                document_id=req.documentId,
                subject_id=req.subjectId,
                field=req.field,
                current_value=req.currentValue,
                proposed_value=req.proposedValue,
                reason=req.reason,
                evidence_description=req.evidenceDescription,
                evidence_reference=req.evidenceReference,
                status=req.status.value if hasattr(req.status, "value") else str(req.status),
                resulting_version=req.resultingVersion,
                reviewer_id=req.reviewerId,
                reviewer_note=req.reviewerNote,
                created_at=req.createdAt,
                decided_at=req.decidedAt,
            )
            s.add(db_c)
        else:
            db_c.status = req.status.value if hasattr(req.status, "value") else str(req.status)
            db_c.resulting_version = req.resultingVersion
            db_c.reviewer_id = req.reviewerId
            db_c.reviewer_note = req.reviewerNote
            db_c.decided_at = req.decidedAt
        return req

    if session:
        return _op(session)
    with get_db_session() as s:
        return _op(s)


def get_correction(request_id: str) -> CorrectionRequestRecord | None:
    with get_db_session() as s:
        r = s.get(CorrectionRequestModel, request_id)
        if r is None:
            return None
        return CorrectionRequestRecord(
            requestId=r.request_id,
            documentId=r.document_id,
            subjectId=r.subject_id,
            field=r.field,
            currentValue=r.current_value,
            proposedValue=r.proposed_value,
            reason=r.reason,
            evidenceDescription=r.evidence_description,
            evidenceReference=r.evidence_reference,
            status=CorrectionStatus(r.status),
            resultingVersion=r.resulting_version,
            reviewerId=r.reviewer_id,
            reviewerNote=r.reviewer_note,
            createdAt=r.created_at,
            decidedAt=r.decided_at,
        )


def list_corrections(document_id: str | None = None) -> list[CorrectionRequestRecord]:
    with get_db_session() as s:
        stmt = select(CorrectionRequestModel)
        if document_id:
            stmt = stmt.where(CorrectionRequestModel.document_id == document_id)
        stmt = stmt.order_by(desc(CorrectionRequestModel.created_at))
        rows = s.scalars(stmt).all()
        return [
            CorrectionRequestRecord(
                requestId=r.request_id,
                documentId=r.document_id,
                subjectId=r.subject_id,
                field=r.field,
                currentValue=r.current_value,
                proposedValue=r.proposed_value,
                reason=r.reason,
                evidenceDescription=r.evidence_description,
                evidenceReference=r.evidence_reference,
                status=CorrectionStatus(r.status),
                resultingVersion=r.resulting_version,
                reviewerId=r.reviewer_id,
                reviewerNote=r.reviewer_note,
                createdAt=r.created_at,
                decidedAt=r.decided_at,
            )
            for r in rows
        ]



# --- Wallet Documents ---

def save_wallet_document(doc: WalletDocument, session: Session | None = None) -> WalletDocument:
    def _op(s: Session) -> WalletDocument:
        db_w = s.get(WalletDocumentModel, doc.documentId)
        if db_w is None:
            db_w = WalletDocumentModel(
                document_id=doc.documentId,
                subject_id="subj_demo_5c7b90",
                title=doc.title,
                document_type=doc.documentType,
                source=doc.source,
                authenticity=doc.authenticity,
                validity_status=doc.validityStatus,
                verification_level=doc.verificationLevel,
                verification_method=doc.verificationMethod,
                current_version=doc.currentVersion,
                issuer=doc.issuer,
                valid_until=doc.validUntil,
                extracted_metadata_json=json.dumps(doc.extractedMetadata),
                created_at=doc.createdAt,
            )
            s.add(db_w)
        else:
            db_w.title = doc.title
            db_w.authenticity = doc.authenticity
            db_w.validity_status = doc.validityStatus
            db_w.verification_level = doc.verificationLevel
            db_w.current_version = doc.currentVersion
            db_w.extracted_metadata_json = json.dumps(doc.extractedMetadata)
        return doc

    if session:
        return _op(session)
    with get_db_session() as s:
        return _op(s)


def list_wallet_documents(subject_id: str = "subj_demo_5c7b90") -> list[WalletDocument]:
    with get_db_session() as s:
        stmt = select(WalletDocumentModel).where(WalletDocumentModel.subject_id == subject_id)
        rows = s.scalars(stmt).all()
        return [
            WalletDocument(
                documentId=r.document_id,
                title=r.title,
                documentType=r.document_type,
                source=r.source,  # type: ignore[arg-type]
                authenticity=r.authenticity,  # type: ignore[arg-type]
                validityStatus=r.validity_status,  # type: ignore[arg-type]
                verificationLevel=r.verification_level,
                verificationMethod=r.verification_method,
                currentVersion=r.current_version,
                issuer=r.issuer,
                validUntil=r.valid_until,
                extractedMetadata=json.loads(r.extracted_metadata_json),
                createdAt=r.created_at,
            )
            for r in rows
        ]


# --- Domain Events ---

def save_domain_event(event: DomainEvent) -> DomainEvent:
    with get_db_session() as s:
        db_e = DomainEventModel(
            event_id=event.eventId,
            event_type=event.type,
            aggregate_id=event.aggregateId,
            actor=event.actor,
            message=event.message,
            created_at=event.createdAt,
        )
        s.add(db_e)
        return event


def list_domain_events() -> list[DomainEvent]:
    with get_db_session() as s:
        stmt = select(DomainEventModel).order_by(desc(DomainEventModel.created_at))
        rows = s.scalars(stmt).all()
        return [
            DomainEvent(
                eventId=r.event_id,
                type=r.event_type,
                aggregateId=r.aggregate_id,
                actor=r.actor,
                message=r.message,
                createdAt=r.created_at,
            )
            for r in rows
        ]


# --- Initial Seed Fixtures ---

def seed_default_data_if_empty() -> None:
    """Populates the database with initial demonstration fixtures if empty."""
    with get_db_session() as s:
        doc_count = s.scalar(select(DocumentModel).limit(1))
        if doc_count is not None:
            return  # Already seeded

        now = datetime.now(UTC)

        # 1. Seed Initial Wallet Documents
        wallet_seeds = [
            WalletDocument(
                documentId="doc_cbse_2026_01",
                title="CBSE Class XII Marksheet (2026)",
                documentType="CLASS_XII",
                source="GOVERNMENT_ISSUED",
                authenticity="VERIFIED",
                validityStatus="ACTIVE",
                verificationLevel=4,
                verificationMethod="Direct Board Registry API Token",
                currentVersion=1,
                issuer="Central Board of Secondary Education (CBSE)",
                validUntil=None,
                extractedMetadata={
                    "student_name": "Sahil Khutey",
                    "roll_number": "99214",
                    "passing_year": 2026,
                    "overall_grade": "A1",
                    "percentage": 94.2,
                },
                createdAt=now,
            ),
            WalletDocument(
                documentId="doc_morth_dl_2021",
                title="Smart Card Driving Licence",
                documentType="DRIVING_LICENCE",
                source="GOVERNMENT_ISSUED",
                authenticity="VERIFIED",
                validityStatus="EXPIRED",
                verificationLevel=4,
                verificationMethod="MoRTH Sarathi National Gateway",
                currentVersion=1,
                issuer="Ministry of Road Transport and Highways",
                validUntil=now,
                extractedMetadata={
                    "holder_name": "Sahil Khutey",
                    "licence_number": "DL-1420210019283",
                    "vehicle_class": "LMV, MCWG",
                    "expired_on": "2025-12-31",
                },
                createdAt=now,
            ),
            WalletDocument(
                documentId="doc_land_deed_1998",
                title="State Land Title Deed (1998)",
                documentType="LAND_RECORD",
                source="LEGACY_RECORD",
                authenticity="VERIFIED",
                validityStatus="ACTIVE",
                verificationLevel=3,
                verificationMethod="Digitised State Revenue Collectorate Archive",
                currentVersion=1,
                issuer="State Revenue Department",
                validUntil=None,
                extractedMetadata={
                    "survey_number": "SUR-98/104",
                    "khasra_number": "442/12",
                    "registered_owner": "Sahil Khutey",
                    "district": "Raipur",
                },
                createdAt=now,
            ),
            WalletDocument(
                documentId="doc_skill_cert_ai",
                title="AI & Cloud Systems Certificate",
                documentType="SKILL_CERTIFICATE",
                source="CITIZEN_UPLOAD",
                authenticity="UNKNOWN",
                validityStatus="ACTIVE",
                verificationLevel=0,
                verificationMethod="Pending Independent Verification",
                currentVersion=1,
                issuer="Self-Declared Vocational Portal",
                validUntil=None,
                extractedMetadata={
                    "student_name": "Sahil Khutey",
                    "course": "Full Stack AI & Cloud Engineering",
                    "issued_year": 2026,
                },
                createdAt=now,
            ),
        ]

        for w in wallet_seeds:
            save_wallet_document(w, s)

        # 2. Seed Initial Department Queue Cases
        case_seeds = [
            VerificationCase(
                caseId="case_cbse_8912",
                documentId="doc_cbse_2026_01",
                claimedIssuer="Central Board of Secondary Education",
                status="UNDER_REVIEW",
                automatedMatchScore=94,
                recommendedAction="Verify claim: 94% score matches Central Examination Board Register.",
                verifierQueue=VerifierQueueId.QUEUE_CBSE,
                createdAt=now,
            ),
            VerificationCase(
                caseId="case_rev_4410",
                documentId="doc_land_deed_1998",
                claimedIssuer="State Revenue Department",
                status="NEEDS_EVIDENCE",
                automatedMatchScore=62,
                recommendedAction="Request mutation entry extract: Khasra number requires Tehsil seal.",
                verifierQueue=VerifierQueueId.QUEUE_REVENUE,
                createdAt=now,
            ),
            VerificationCase(
                caseId="case_trans_9021",
                documentId="doc_morth_dl_2021",
                claimedIssuer="Ministry of Road Transport",
                status="UNDER_REVIEW",
                automatedMatchScore=88,
                recommendedAction="Verify DL authenticity: valid license but expired validity period.",
                verifierQueue=VerifierQueueId.QUEUE_TRANSPORT,
                createdAt=now,
            ),
            VerificationCase(
                caseId="case_gen_1102",
                documentId="doc_skill_cert_ai",
                claimedIssuer="Self-Declared Vocational Portal",
                status="NEW",
                automatedMatchScore=45,
                recommendedAction="Manual review required: unrecognised training institution accreditation.",
                verifierQueue=VerifierQueueId.QUEUE_GENERAL,
                createdAt=now,
            ),
        ]

        for c in case_seeds:
            save_verification_case(c, s)


def update_document_verification_level(
    document_id: str,
    level: int = 4,
    authenticity: str = "VERIFIED",
    method: str = "Authorised Aadhaar eKYC Demographics & Registry Match",
) -> None:
    """Elevates document and wallet verification level in persistent storage upon eKYC verification."""
    with get_db_session() as s:
        d = s.get(DocumentModel, document_id)
        if d:
            d.verification_level = level
            d.authenticity = authenticity
        w = s.get(WalletDocumentModel, document_id)
        if w:
            w.verification_level = level
            w.authenticity = authenticity
            w.verification_method = method

