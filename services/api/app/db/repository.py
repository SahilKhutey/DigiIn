"""Database repository layer providing CRUD operations and seed data management."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models import (
    AuthChallengeModel,
    CorrectionRequestModel,
    CredentialModel,
    DigiInAccountModel,
    DocumentClaimModel,
    DocumentModel,
    DocumentVersionModel,
    DomainEventModel,
    GatewayConsentModel,
    GatewayVerificationRequestModel,
    IdentityClaimModel,
    ProcessingJobModel,
    SecurityEventModel,
    SessionModel,
    VerificationCaseModel,
    WalletDocumentModel,
)
from app.db.session import get_db_session
from app.domain.auth_models import (
    AuthChallengeRecord,
    DigiInAccountRecord,
    IdentityClaimRecord,
    SecurityEventRecord,
    SessionRecord,
)
from app.domain.credential_models import (
    Credential,
    CredentialStatus,
    VerifiedClaim,
)
from app.domain.gateway_models import (
    Consent,
    RequestStatus,
)
from app.domain.gateway_models import (
    VerificationRequest as GatewayVerificationRequest,
)
from app.domain.models import (
    CorrectionRequestRecord,
    CorrectionStatus,
    DocumentClaimRecord,
    DocumentVersionRecord,
    DocumentVersionStatus,
    DomainEvent,
    GovernmentReviewDecision,
    ProcessingJobRecord,
    UploadedDocument,
    VerificationCase,
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
                owner_account_id=v.ownerAccountId,
                version_number=v.versionNumber,
                parent_version_id=v.parentVersionId,
                object_id=v.objectId,
                sha256=v.sha256,
                content_type=v.contentType,
                size_bytes=v.sizeBytes,
                processing_status=v.processingStatus,
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
            if v.processingStatus:
                db_v.processing_status = v.processingStatus
            if v.objectId:
                db_v.object_id = v.objectId
            if v.sha256:
                db_v.sha256 = v.sha256
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
                ownerAccountId=r.owner_account_id,
                versionNumber=r.version_number,
                parentVersionId=r.parent_version_id,
                objectId=r.object_id,
                sha256=r.sha256,
                contentType=r.content_type,
                sizeBytes=r.size_bytes,
                processingStatus=r.processing_status or "completed",
                status=DocumentVersionStatus(r.status),
                metadata=json.loads(r.metadata_json) if r.metadata_json else {},
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
                ownerAccountId=r.owner_account_id,
                versionNumber=r.version_number,
                parentVersionId=r.parent_version_id,
                objectId=r.object_id,
                sha256=r.sha256,
                contentType=r.content_type,
                sizeBytes=r.size_bytes,
                processingStatus=r.processing_status or "completed",
                status=DocumentVersionStatus(r.status),
                metadata=json.loads(r.metadata_json) if r.metadata_json else {},
                changeSummary=r.change_summary,
                authority=r.authority,
                evidenceReference=r.evidence_reference,
                createdAt=r.created_at,
                supersededAt=r.superseded_at,
            )
            for r in rows
        ]


# --- Processing Jobs & Claims ---

def save_processing_job(job: ProcessingJobRecord, session: Session | None = None) -> ProcessingJobRecord:
    def _op(s: Session) -> ProcessingJobRecord:
        db_job = s.get(ProcessingJobModel, job.jobId)
        if db_job is None:
            db_job = ProcessingJobModel(
                job_id=job.jobId,
                document_id=job.documentId,
                version_id=job.versionId,
                owner_account_id=job.ownerAccountId,
                status=job.status,
                malware_scan_json=json.dumps(job.malwareScan) if job.malwareScan else None,
                ocr_result_json=json.dumps(job.ocrResult) if job.ocrResult else None,
                claims_json=json.dumps(job.claims) if job.claims else None,
                error_message=job.errorMessage,
                created_at=job.createdAt,
                completed_at=job.completedAt,
            )
            s.add(db_job)
        else:
            db_job.status = job.status
            db_job.malware_scan_json = json.dumps(job.malwareScan) if job.malwareScan else None
            db_job.ocr_result_json = json.dumps(job.ocrResult) if job.ocrResult else None
            db_job.claims_json = json.dumps(job.claims) if job.claims else None
            db_job.error_message = job.errorMessage
            db_job.completed_at = job.completedAt
        return job

    if session:
        return _op(session)
    with get_db_session() as s:
        return _op(s)


def get_processing_job(job_id: str) -> ProcessingJobRecord | None:
    with get_db_session() as s:
        row = s.get(ProcessingJobModel, job_id)
        if row is None:
            return None
        return ProcessingJobRecord(
            jobId=row.job_id,
            documentId=row.document_id,
            versionId=row.version_id,
            ownerAccountId=row.owner_account_id,
            status=row.status,
            malwareScan=json.loads(row.malware_scan_json) if row.malware_scan_json else None,
            ocrResult=json.loads(row.ocr_result_json) if row.ocr_result_json else None,
            claims=json.loads(row.claims_json) if row.claims_json else [],
            errorMessage=row.error_message,
            createdAt=row.created_at,
            completedAt=row.completed_at,
        )


def save_document_claim(claim: DocumentClaimRecord, session: Session | None = None) -> DocumentClaimRecord:
    def _op(s: Session) -> DocumentClaimRecord:
        db_c = s.get(DocumentClaimModel, claim.claimId)
        if db_c is None:
            db_c = DocumentClaimModel(
                claim_id=claim.claimId,
                document_id=claim.documentId,
                version_id=claim.versionId,
                claim_key=claim.claimKey,
                claim_value=claim.claimValue,
                confidence=claim.confidence,
                created_at=claim.createdAt,
            )
            s.add(db_c)
        else:
            db_c.claim_value = claim.claimValue
            db_c.confidence = claim.confidence
        return claim

    if session:
        return _op(session)
    with get_db_session() as s:
        return _op(s)


def get_document_claims(document_id: str) -> list[DocumentClaimRecord]:
    with get_db_session() as s:
        stmt = (
            select(DocumentClaimModel)
            .where(DocumentClaimModel.document_id == document_id)
            .order_by(DocumentClaimModel.created_at)
        )
        rows = s.scalars(stmt).all()
        return [
            DocumentClaimRecord(
                claimId=r.claim_id,
                documentId=r.document_id,
                versionId=r.version_id,
                claimKey=r.claim_key,
                claimValue=r.claim_value,
                confidence=r.confidence,
                createdAt=r.created_at,
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


# --- Phase 3: Identity & Authentication Repository ---

def save_account(acc: DigiInAccountRecord, session: Session | None = None) -> DigiInAccountRecord:
    now = datetime.now(UTC)

    def _op(s: Session) -> DigiInAccountRecord:
        db_acc = s.get(DigiInAccountModel, acc.id)
        if db_acc is None:
            db_acc = DigiInAccountModel(
                id=acc.id,
                account_id=acc.account_id,
                phone_number=acc.phone_number,
                role=acc.role,
                status=acc.status,
                created_at=acc.created_at or now,
                updated_at=acc.updated_at or now,
            )
            s.add(db_acc)
        else:
            db_acc.status = acc.status
            db_acc.role = acc.role
            db_acc.updated_at = now
        return acc

    if session:
        return _op(session)
    with get_db_session() as s:
        return _op(s)


def get_account_by_id(account_id: str) -> DigiInAccountRecord | None:
    with get_db_session() as s:
        stmt = select(DigiInAccountModel).where(
            (DigiInAccountModel.account_id == account_id) | (DigiInAccountModel.id == account_id)
        )
        row = s.scalars(stmt).first()
        if row is None:
            return None
        return DigiInAccountRecord(
            id=row.id,
            account_id=row.account_id,
            phone_number=row.phone_number,
            role=row.role,
            status=row.status,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


def get_account_by_phone(phone_number: str) -> DigiInAccountRecord | None:
    clean_phone = phone_number.strip()
    with get_db_session() as s:
        stmt = select(DigiInAccountModel).where(DigiInAccountModel.phone_number == clean_phone)
        row = s.scalars(stmt).first()
        if row is None:
            return None
        return DigiInAccountRecord(
            id=row.id,
            account_id=row.account_id,
            phone_number=row.phone_number,
            role=row.role,
            status=row.status,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


def save_identity_claim(claim: IdentityClaimRecord, session: Session | None = None) -> IdentityClaimRecord:
    now = datetime.now(UTC)

    def _op(s: Session) -> IdentityClaimRecord:
        db_c = s.get(IdentityClaimModel, claim.id)
        if db_c is None:
            db_c = IdentityClaimModel(
                id=claim.id,
                account_id=claim.account_id,
                claim_type=claim.claim_type,
                value_reference=claim.value_reference,
                verification_level=claim.verification_level,
                source=claim.source,
                verified_at=claim.verified_at or now,
            )
            s.add(db_c)
        else:
            db_c.verification_level = claim.verification_level
            db_c.verified_at = claim.verified_at or now
        return claim

    if session:
        return _op(session)
    with get_db_session() as s:
        return _op(s)


def get_identity_claims(account_id: str) -> list[IdentityClaimRecord]:
    with get_db_session() as s:
        stmt = (
            select(IdentityClaimModel)
            .where(IdentityClaimModel.account_id == account_id)
            .order_by(IdentityClaimModel.verified_at)
        )
        rows = s.scalars(stmt).all()
        return [
            IdentityClaimRecord(
                id=r.id,
                account_id=r.account_id,
                claim_type=r.claim_type,
                value_reference=r.value_reference,
                verification_level=r.verification_level,
                source=r.source,
                verified_at=r.verified_at,
            )
            for r in rows
        ]


def save_auth_challenge(ch: AuthChallengeRecord, session: Session | None = None) -> AuthChallengeRecord:
    def _op(s: Session) -> AuthChallengeRecord:
        db_ch = s.get(AuthChallengeModel, ch.challenge_id)
        if db_ch is None:
            db_ch = AuthChallengeModel(
                id=ch.challenge_id,
                account_id=ch.account_id,
                channel=ch.channel,
                challenge_hash=ch.challenge_hash,
                expires_at=ch.expires_at,
                attempts=ch.attempts,
                consumed_at=ch.consumed_at,
            )
            s.add(db_ch)
        else:
            db_ch.attempts = ch.attempts
            db_ch.consumed_at = ch.consumed_at
        return ch

    if session:
        return _op(session)
    with get_db_session() as s:
        return _op(s)


def get_auth_challenge(challenge_id: str) -> AuthChallengeRecord | None:
    with get_db_session() as s:
        row = s.get(AuthChallengeModel, challenge_id)
        if row is None:
            return None
        return AuthChallengeRecord(
            challenge_id=row.id,
            account_id=row.account_id,
            channel=row.channel,
            challenge_hash=row.challenge_hash,
            expires_at=row.expires_at,
            attempts=row.attempts,
            consumed_at=row.consumed_at,
        )


def save_session(sess: SessionRecord, session: Session | None = None) -> SessionRecord:
    now = datetime.now(UTC)

    def _op(s: Session) -> SessionRecord:
        db_s = s.get(SessionModel, sess.session_id)
        if db_s is None:
            db_s = SessionModel(
                id=sess.session_id,
                account_id=sess.account_id,
                token_family=sess.token_family,
                refresh_token_hash=sess.refresh_token_hash,
                created_at=sess.created_at or now,
                expires_at=sess.expires_at,
                revoked_at=sess.revoked_at,
                last_used_at=sess.last_used_at or now,
            )
            s.add(db_s)
        else:
            db_s.refresh_token_hash = sess.refresh_token_hash
            db_s.revoked_at = sess.revoked_at
            db_s.last_used_at = sess.last_used_at or now
        return sess

    if session:
        return _op(session)
    with get_db_session() as s:
        return _op(s)


def get_session(session_id: str) -> SessionRecord | None:
    with get_db_session() as s:
        row = s.get(SessionModel, session_id)
        if row is None:
            return None
        return SessionRecord(
            session_id=row.id,
            account_id=row.account_id,
            token_family=row.token_family,
            refresh_token_hash=row.refresh_token_hash,
            created_at=row.created_at,
            expires_at=row.expires_at,
            revoked_at=row.revoked_at,
            last_used_at=row.last_used_at,
        )


def get_sessions_by_family(token_family: str) -> list[SessionRecord]:
    with get_db_session() as s:
        stmt = (
            select(SessionModel)
            .where(SessionModel.token_family == token_family)
            .order_by(SessionModel.created_at)
        )
        rows = s.scalars(stmt).all()
        return [
            SessionRecord(
                session_id=r.id,
                account_id=r.account_id,
                token_family=r.token_family,
                refresh_token_hash=r.refresh_token_hash,
                created_at=r.created_at,
                expires_at=r.expires_at,
                revoked_at=r.revoked_at,
                last_used_at=r.last_used_at,
            )
            for r in rows
        ]


def revoke_session(session_id: str) -> None:
    now = datetime.now(UTC)
    with get_db_session() as s:
        row = s.get(SessionModel, session_id)
        if row and not row.revoked_at:
            row.revoked_at = now


def revoke_token_family(token_family: str) -> None:
    now = datetime.now(UTC)
    with get_db_session() as s:
        stmt = select(SessionModel).where(
            (SessionModel.token_family == token_family) & (SessionModel.revoked_at.is_(None))
        )
        rows = s.scalars(stmt).all()
        for r in rows:
            r.revoked_at = now


def save_security_event(evt: SecurityEventRecord, session: Session | None = None) -> SecurityEventRecord:
    def _op(s: Session) -> SecurityEventRecord:
        db_evt = SecurityEventModel(
            id=evt.id,
            account_id=evt.account_id,
            event_type=evt.event_type,
            timestamp=evt.timestamp,
            request_id=evt.request_id,
            metadata_json=json.dumps(evt.metadata or {}),
        )
        s.add(db_evt)
        return evt

    if session:
        return _op(session)
    with get_db_session() as s:
        return _op(s)


def list_security_events(account_id: str | None = None, limit: int = 50) -> list[SecurityEventRecord]:
    with get_db_session() as s:
        stmt = select(SecurityEventModel).order_by(desc(SecurityEventModel.timestamp))
        if account_id:
            stmt = stmt.where(SecurityEventModel.account_id == account_id)
        rows = s.scalars(stmt.limit(limit)).all()
        return [
            SecurityEventRecord(
                id=r.id,
                account_id=r.account_id,
                event_type=r.event_type,
                timestamp=r.timestamp,
                request_id=r.request_id,
                metadata=json.loads(r.metadata_json) if r.metadata_json else {},
            )
            for r in rows
        ]


# --- Phase 4: Credential Engine Repository ---

def save_credential(c: Credential, session: Session | None = None) -> Credential:
    claims_data = [
        {
            "claim_type": cl.claim_type,
            "value": cl.value,
            "source": cl.source,
            "verification_level": cl.verification_level,
            "verified_at": cl.verified_at.isoformat() if cl.verified_at else None,
        }
        for cl in c.claims
    ]

    def _op(s: Session) -> Credential:
        db_c = s.get(CredentialModel, c.credential_id)
        if db_c is None:
            db_c = CredentialModel(
                credential_id=c.credential_id,
                account_id=c.account_id,
                credential_type=c.credential_type,
                issuer=c.issuer,
                claims_json=json.dumps(claims_data),
                issued_at=c.issued_at,
                expires_at=c.expires_at,
                status=c.status.value if hasattr(c.status, "value") else str(c.status),
                verification_case_id=c.verification_case_id,
            )
            s.add(db_c)
        else:
            db_c.status = c.status.value if hasattr(c.status, "value") else str(c.status)
            db_c.expires_at = c.expires_at
        return c

    if session:
        return _op(session)
    with get_db_session() as s:
        return _op(s)


def get_credential_by_id(credential_id: str) -> Credential | None:
    with get_db_session() as s:
        row = s.get(CredentialModel, credential_id)
        if row is None:
            return None
        raw_claims = json.loads(row.claims_json) if row.claims_json else []
        claims = tuple(
            VerifiedClaim(
                claim_type=item["claim_type"],
                value=item["value"],
                source=item["source"],
                verification_level=item.get("verification_level", "verified"),
                verified_at=datetime.fromisoformat(item["verified_at"]) if item.get("verified_at") else row.issued_at,
            )
            for item in raw_claims
        )
        return Credential(
            credential_id=row.credential_id,
            account_id=row.account_id,
            credential_type=row.credential_type,
            issuer=row.issuer,
            claims=claims,
            issued_at=row.issued_at,
            expires_at=row.expires_at,
            status=CredentialStatus(row.status),
            verification_case_id=row.verification_case_id,
        )


def list_credentials_for_account(account_id: str) -> list[Credential]:
    with get_db_session() as s:
        stmt = (
            select(CredentialModel)
            .where(CredentialModel.account_id == account_id)
            .order_by(desc(CredentialModel.issued_at))
        )
        rows = s.scalars(stmt).all()
        result: list[Credential] = []
        for row in rows:
            raw_claims = json.loads(row.claims_json) if row.claims_json else []
            claims = tuple(
                VerifiedClaim(
                    claim_type=item["claim_type"],
                    value=item["value"],
                    source=item["source"],
                    verification_level=item.get("verification_level", "verified"),
                    verified_at=datetime.fromisoformat(item["verified_at"]) if item.get("verified_at") else row.issued_at,
                )
                for item in raw_claims
            )
            result.append(
                Credential(
                    credential_id=row.credential_id,
                    account_id=row.account_id,
                    credential_type=row.credential_type,
                    issuer=row.issuer,
                    claims=claims,
                    issued_at=row.issued_at,
                    expires_at=row.expires_at,
                    status=CredentialStatus(row.status),
                    verification_case_id=row.verification_case_id,
                )
            )
        return result


def update_credential_status(credential_id: str, status: CredentialStatus) -> None:
    with get_db_session() as s:
        row = s.get(CredentialModel, credential_id)
        if row:
            row.status = status.value if hasattr(status, "value") else str(status)


def revoke_credential(credential_id: str) -> None:
    update_credential_status(credential_id, CredentialStatus.REVOKED)


# --- Phase 5: Verification Gateway Repository ---

def save_gateway_request(
    req: GatewayVerificationRequest,
    session: Session | None = None,
) -> GatewayVerificationRequest:
    now = datetime.now(UTC)

    def _op(s: Session) -> GatewayVerificationRequest:
        db_req = s.get(GatewayVerificationRequestModel, req.request_id)
        if db_req is None:
            db_req = GatewayVerificationRequestModel(
                request_id=req.request_id,
                verifier_id=req.verifier_id,
                account_id=req.account_id,
                purpose=req.purpose,
                requested_claim_types_json=json.dumps(list(req.requested_claim_types)),
                status=req.status.value if hasattr(req.status, "value") else str(req.status),
                expires_at=req.expires_at,
                created_at=req.created_at or now,
            )
            s.add(db_req)
        else:
            db_req.status = req.status.value if hasattr(req.status, "value") else str(req.status)
        return req

    if session:
        return _op(session)
    with get_db_session() as s:
        return _op(s)


def get_gateway_request(request_id: str) -> GatewayVerificationRequest | None:
    with get_db_session() as s:
        row = s.get(GatewayVerificationRequestModel, request_id)
        if row is None:
            return None
        claims = tuple(json.loads(row.requested_claim_types_json)) if row.requested_claim_types_json else ()
        return GatewayVerificationRequest(
            request_id=row.request_id,
            verifier_id=row.verifier_id,
            account_id=row.account_id,
            purpose=row.purpose,
            requested_claim_types=claims,
            status=RequestStatus(row.status),
            expires_at=row.expires_at,
            created_at=row.created_at,
        )


def list_gateway_requests_for_account(account_id: str) -> list[GatewayVerificationRequest]:
    with get_db_session() as s:
        stmt = (
            select(GatewayVerificationRequestModel)
            .where(GatewayVerificationRequestModel.account_id == account_id)
            .order_by(desc(GatewayVerificationRequestModel.created_at))
        )
        rows = s.scalars(stmt).all()
        return [
            GatewayVerificationRequest(
                request_id=row.request_id,
                verifier_id=row.verifier_id,
                account_id=row.account_id,
                purpose=row.purpose,
                requested_claim_types=tuple(json.loads(row.requested_claim_types_json)) if row.requested_claim_types_json else (),
                status=RequestStatus(row.status),
                expires_at=row.expires_at,
                created_at=row.created_at,
            )
            for row in rows
        ]


def update_gateway_request_status(request_id: str, status: RequestStatus) -> None:
    with get_db_session() as s:
        row = s.get(GatewayVerificationRequestModel, request_id)
        if row:
            row.status = status.value if hasattr(status, "value") else str(status)


def save_gateway_consent(c: Consent, session: Session | None = None) -> Consent:
    def _op(s: Session) -> Consent:
        db_c = s.get(GatewayConsentModel, c.consent_id)
        if db_c is None:
            db_c = GatewayConsentModel(
                consent_id=c.consent_id,
                request_id=c.request_id,
                account_id=c.account_id,
                decision=c.decision,
                approved_claim_types_json=json.dumps(list(c.approved_claim_types)),
                granted_at=c.granted_at,
                expires_at=c.expires_at,
                revoked_at=c.revoked_at,
            )
            s.add(db_c)
        else:
            db_c.decision = c.decision
            db_c.approved_claim_types_json = json.dumps(list(c.approved_claim_types))
            db_c.revoked_at = c.revoked_at
        return c

    if session:
        return _op(session)
    with get_db_session() as s:
        return _op(s)


def get_gateway_consent_by_request(request_id: str) -> Consent | None:
    with get_db_session() as s:
        stmt = select(GatewayConsentModel).where(GatewayConsentModel.request_id == request_id)
        row = s.scalars(stmt).first()
        if row is None:
            return None
        claims = tuple(json.loads(row.approved_claim_types_json)) if row.approved_claim_types_json else ()
        return Consent(
            consent_id=row.consent_id,
            request_id=row.request_id,
            account_id=row.account_id,
            decision=row.decision,
            approved_claim_types=claims,
            granted_at=row.granted_at,
            expires_at=row.expires_at,
            revoked_at=row.revoked_at,
        )


def revoke_gateway_consent(request_id: str) -> None:
    now = datetime.now(UTC)
    with get_db_session() as s:
        stmt = select(GatewayConsentModel).where(GatewayConsentModel.request_id == request_id)
        row = s.scalars(stmt).first()
        if row and row.revoked_at is None:
            row.revoked_at = now
        req_row = s.get(GatewayVerificationRequestModel, request_id)
        if req_row:
            req_row.status = RequestStatus.REVOKED.value



