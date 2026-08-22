"""Runnable in-memory platform foundation for the DigiIn vertical slice."""

from __future__ import annotations

import hashlib
import sys
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import app.db.repository as repo
from app.domain.models import (
    AuthenticityStatus,
    CorrectionDecisionType,
    CorrectionRequestCreate,
    CorrectionRequestRecord,
    CorrectionReviewDecision,
    CorrectionStatus,
    DirectUploadPayload,
    DisclosureMode,
    DocumentClassificationResult,
    DocumentSource,
    DocumentUploadRequest,
    DocumentVersionRecord,
    DocumentVersionStatus,
    DomainEvent,
    EvidenceComparisonDetail,
    FeatureFlag,
    FieldComparison,
    GovernmentReviewDecision,
    MockIntegrationState,
    PipelineUploadResponse,
    PlatformSnapshot,
    PlatformTransaction,
    PolicyDefinition,
    PolicyRequirement,
    StudentDemoResult,
    UploadedDocument,
    ValidityStatus,
    VerificationAuthorization,
    VerificationCase,
    VerificationRequestCreate,
    VerificationRequirement,
    VerifierQueueId,
    VerifierQueueSummary,
    WalletDocument,
)
from app.services.verification import authorize_verification_request, create_verification_request

DOCUMENTS: dict[str, UploadedDocument] = {}
VERSIONS: dict[str, list[DocumentVersionRecord]] = {}
CORRECTIONS: dict[str, CorrectionRequestRecord] = {}
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
        key="FEATURE_DOCUMENT_CORRECTIONS",
        enabled=True,
        description="Enables citizen correction requests, review workflows, and immutable versioning.",
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


def ensure_seed_documents() -> None:
    now = datetime.now(UTC)

    # 1. Class XII Marksheet (Government Issued, Verified, Level 4, Active)
    if "doc_cbse_xii_2026" not in DOCUMENTS:
        doc1 = UploadedDocument(
            documentId="doc_cbse_xii_2026",
            ownerSubjectId="subj_demo_5c7b90",
            documentType="CLASS_XII",
            source="GOVERNMENT_ISSUED",
            filename="cbse_class_xii_marksheet.pdf",
            status="VERIFIED",
            authenticity="VERIFIED",
            verificationLevel=4,
            currentVersion=1,
            extractedMetadata={
                "student_name": "SAHIL KHUTEY",
                "roll_number": "CBSE-2026-99214",
                "passing_year": 2026,
                "percentage": 94.2,
                "qualification": "Class XII Science",
            },
            createdAt=now,
        )
        DOCUMENTS[doc1.documentId] = doc1
        VERSIONS[doc1.documentId] = [
            DocumentVersionRecord(
                versionId="ver_cbse_v1_001",
                versionNumber=1,
                documentId=doc1.documentId,
                status=DocumentVersionStatus.ACTIVE,
                metadata=doc1.extractedMetadata,
                changeSummary="Official electronic certificate issued by Central Board of Secondary Education.",
                authority="Central Board of Secondary Education (CBSE)",
                createdAt=now,
            )
        ]

    # 2. Motor Driving Licence (Government Issued, Verified, Level 5, EXPIRED)
    if "doc_dl_morth_9811" not in DOCUMENTS:
        doc2 = UploadedDocument(
            documentId="doc_dl_morth_9811",
            ownerSubjectId="subj_demo_5c7b90",
            documentType="DRIVING_LICENCE",
            source="GOVERNMENT_ISSUED",
            filename="driving_licence_morth.pdf",
            status="VERIFIED",
            authenticity="VERIFIED",
            verificationLevel=5,
            currentVersion=1,
            extractedMetadata={
                "licence_number": "DL-1420210019283",
                "holder_name": "SAHIL KHUTEY",
                "vehicle_classes": ["LMV", "MCWG"],
                "valid_till": "2025-12-31",
                "status": "EXPIRED",
            },
            createdAt=now,
        )
        DOCUMENTS[doc2.documentId] = doc2
        VERSIONS[doc2.documentId] = [
            DocumentVersionRecord(
                versionId="ver_dl_v1_001",
                versionNumber=1,
                documentId=doc2.documentId,
                status=DocumentVersionStatus.ACTIVE,
                metadata=doc2.extractedMetadata,
                changeSummary="Cryptographically signed Sarathi Driving Licence credential issued by MoRTH.",
                authority="Ministry of Road Transport and Highways (MoRTH)",
                createdAt=now,
            )
        ]

    # 3. Pre-2000 Archival Land Record (Legacy Record, Verified, Level 4, Active)
    if "doc_land_revenue_1998" not in DOCUMENTS:
        doc3 = UploadedDocument(
            documentId="doc_land_revenue_1998",
            ownerSubjectId="subj_demo_5c7b90",
            documentType="LAND_RECORD",
            source="LEGACY_RECORD",
            filename="revenue_archive_land_deed_1998.pdf",
            status="VERIFIED",
            authenticity="VERIFIED",
            verificationLevel=4,
            currentVersion=1,
            extractedMetadata={
                "survey_number": "SUR-98/104",
                "khasra_no": "442/12",
                "tehsil": "Raipur Central",
                "year": 1998,
                "district": "Raipur",
            },
            createdAt=now,
        )
        DOCUMENTS[doc3.documentId] = doc3
        VERSIONS[doc3.documentId] = [
            DocumentVersionRecord(
                versionId="ver_land_v1_001",
                versionNumber=1,
                documentId=doc3.documentId,
                status=DocumentVersionStatus.ACTIVE,
                metadata=doc3.extractedMetadata,
                changeSummary="Archival physical register audit and digitization approved by District Collectorate.",
                authority="State Land & Revenue Records Department",
                createdAt=now,
            )
        ]

    # 4. Uploaded Skill Certificate (Citizen Upload, Authenticity UNKNOWN, Level 0, Active)
    if "doc_upload_skill_7731" not in DOCUMENTS:
        doc4 = UploadedDocument(
            documentId="doc_upload_skill_7731",
            ownerSubjectId="subj_demo_5c7b90",
            documentType="SKILL_CERTIFICATE",
            source="CITIZEN_UPLOAD",
            filename="ai_engineering_certificate.pdf",
            status="UPLOADED",
            authenticity="UNKNOWN",
            verificationLevel=0,
            currentVersion=1,
            extractedMetadata={
                "file_name": "ai_engineering_certificate.pdf",
                "file_size_kb": 320,
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            },
            createdAt=now,
        )
        DOCUMENTS[doc4.documentId] = doc4
        VERSIONS[doc4.documentId] = [
            DocumentVersionRecord(
                versionId="ver_skill_v1_001",
                versionNumber=1,
                documentId=doc4.documentId,
                status=DocumentVersionStatus.ACTIVE,
                metadata=doc4.extractedMetadata,
                changeSummary="Citizen-uploaded PDF document. Trust not established.",
                authority="Unverified Issuer",
                createdAt=now,
            )
        ]

    # Seed Multi-Tenant Verification Cases
    if "case_cbse_001" not in CASES:
        CASES["case_cbse_001"] = VerificationCase(
            caseId="case_cbse_001",
            documentId="doc_cbse_xii_2026",
            claimedIssuer="Central Board of Secondary Education (CBSE)",
            status="UNDER_REVIEW",
            automatedMatchScore=94,
            recommendedAction="Match confidence is high (94%). Recommended action: Approve & Verify as Level 4.",
            verifierQueue=VerifierQueueId.QUEUE_CBSE,
            createdAt=now,
        )
    if "case_revenue_001" not in CASES:
        CASES["case_revenue_001"] = VerificationCase(
            caseId="case_revenue_001",
            documentId="doc_land_revenue_1998",
            claimedIssuer="State Revenue & Land Records Department",
            status="UNDER_REVIEW",
            automatedMatchScore=88,
            recommendedAction="Archival survey number and tehsil matched in District 1998 Land Register.",
            verifierQueue=VerifierQueueId.QUEUE_REVENUE,
            createdAt=now,
        )
    if "case_transport_001" not in CASES:
        CASES["case_transport_001"] = VerificationCase(
            caseId="case_transport_001",
            documentId="doc_dl_morth_9811",
            claimedIssuer="Ministry of Road Transport & Highways (MoRTH)",
            status="NEEDS_EVIDENCE",
            automatedMatchScore=72,
            recommendedAction="Licence validity expired on 2025-12-31. Request renewal certificate or transfer.",
            verifierQueue=VerifierQueueId.QUEUE_TRANSPORT,
            createdAt=now,
        )
    if "case_skill_001" not in CASES:
        CASES["case_skill_001"] = VerificationCase(
            caseId="case_skill_001",
            documentId="doc_upload_skill_7731",
            claimedIssuer="Unverified Self-Issued Training Portal",
            status="NEW",
            automatedMatchScore=45,
            recommendedAction="Raw citizen upload. No accredited issuer signature detected. Manual audit required.",
            verifierQueue=VerifierQueueId.QUEUE_GENERAL,
            createdAt=now,
        )




def get_wallet_documents(subject_id: str = "subj_demo_5c7b90") -> list[WalletDocument]:
    ensure_seed_documents()
    wallet: list[WalletDocument] = []

    for doc in DOCUMENTS.values():
        title = _doc_title(doc.documentType, doc.extractedMetadata)
        issuer = _doc_issuer(doc.documentType, doc.source)
        method = _doc_verification_method(doc.verificationLevel, doc.source, doc.status)

        if doc.extractedMetadata.get("status") == "EXPIRED" or doc.documentType == "DRIVING_LICENCE":
            validity_status = ValidityStatus.EXPIRED
        elif doc.status == "REJECTED":
            validity_status = ValidityStatus.REVOKED
        else:
            validity_status = ValidityStatus.ACTIVE

        wallet_doc = WalletDocument(
            documentId=doc.documentId,
            title=title,
            documentType=doc.documentType,
            source=DocumentSource(doc.source),
            authenticity=AuthenticityStatus(doc.authenticity),
            validityStatus=validity_status,
            verificationLevel=doc.verificationLevel,
            verificationMethod=method,
            currentVersion=doc.currentVersion,
            issuer=issuer,
            validUntil=datetime(2025, 12, 31, 23, 59, 59, tzinfo=UTC)
            if validity_status == ValidityStatus.EXPIRED
            else None,
            extractedMetadata=doc.extractedMetadata,
            createdAt=doc.createdAt,
        )
        wallet.append(wallet_doc)

    return wallet


def platform_snapshot() -> PlatformSnapshot:
    ensure_seed_documents()
    all_versions: list[DocumentVersionRecord] = []
    for ver_list in VERSIONS.values():
        all_versions.extend(ver_list)
    return PlatformSnapshot(
        featureFlags=FEATURE_FLAGS,
        policies=POLICIES,
        mockIntegrations=MOCK_INTEGRATIONS,
        documents=list(DOCUMENTS.values()),
        versions=all_versions,
        verificationCases=list(CASES.values()),
        corrections=list(CORRECTIONS.values()),
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
        currentVersion=1,
        extractedMetadata={},
        createdAt=now,
    )
    DOCUMENTS[document.documentId] = document
    repo.save_document(document)

    initial_version = DocumentVersionRecord(
        versionId=f"ver_{uuid4().hex[:12]}",
        versionNumber=1,
        documentId=document.documentId,
        parentVersionId=None,
        status=DocumentVersionStatus.ACTIVE,
        metadata={},
        changeSummary="Initial document registration.",
        authority=_claimed_issuer(document.documentType),
        createdAt=now,
    )
    VERSIONS[document.documentId] = [initial_version]
    repo.save_document_version(initial_version)

    _event("DocumentUploaded", document.documentId, payload.ownerSubjectId, "Document metadata accepted.")
    _event("DocumentVersionCreated", initial_version.versionId, payload.ownerSubjectId, f"Initial version v1 registered for {document.documentId}.")
    return document



def upload_and_classify_pipeline(payload: DirectUploadPayload) -> PipelineUploadResponse:
    ensure_seed_documents()
    now = datetime.now(UTC)
    doc_id = f"doc_{uuid4().hex[:12]}"
    owner_id = payload.ownerSubjectId or "subj_demo_5c7b90"
    filename = payload.filename
    content_bytes = (payload.simulatedContent or f"{filename}_{now.isoformat()}").encode("utf-8")
    sha256_hash = hashlib.sha256(content_bytes).hexdigest()

    fn_lower = filename.lower()
    hint = (payload.documentTypeHint or "").upper()

    if hint == "CLASS_XII" or (not hint and any(k in fn_lower for k in ["cbse", "xii", "marksheet", "school", "education"])):
        doc_type = "CLASS_XII"
        confidence = 94
        issuer = "Central Board of Secondary Education (CBSE)"
        queue = VerifierQueueId.QUEUE_CBSE
        extracted = {
            "student_name": "SAHIL KHUTEY",
            "roll_number": "CBSE-2026-99214",
            "passing_year": "2026",
            "percentage": "94.2",
            "qualification": "Class XII Science",
            "institution": "Delhi Public Senior Secondary School",
        }
        notes = [
            "Standard CBSE hologram watermark and QR digest verified.",
            "All grade attributes and subjects successfully parsed.",
        ]
    elif hint == "LAND_RECORD" or (not hint and any(k in fn_lower for k in ["land", "deed", "revenue", "property"])):
        doc_type = "LAND_RECORD"
        confidence = 88
        issuer = "State Revenue & Land Records Department"
        queue = VerifierQueueId.QUEUE_REVENUE
        extracted = {
            "survey_number": "SUR-98/104",
            "khasra_no": "442/12",
            "tehsil": "Raipur Central",
            "district": "Raipur",
            "year": "1998",
            "recorded_owner": "SAHIL KHUTEY",
            "area_hectares": "1.450",
            "land_use_type": "Agricultural / Non-Encumbered",
        }
        notes = [
            "Archival seal and revenue stamp detected with high fidelity.",
            "Historical tehsil boundaries mapped to 1998 gazette records.",
        ]
    elif hint == "DRIVING_LICENCE" or (not hint and any(k in fn_lower for k in ["dl", "licence", "driving", "transport"])):
        doc_type = "DRIVING_LICENCE"
        confidence = 82
        issuer = "Ministry of Road Transport & Highways (MoRTH)"
        queue = VerifierQueueId.QUEUE_TRANSPORT
        extracted = {
            "licence_number": "DL-1420210019283",
            "holder_name": "SAHIL KHUTEY",
            "vehicle_classes": "LMV, MCWG",
            "valid_till": "2025-12-31",
            "rto_jurisdiction": "DL-14 South Delhi Regional Transport Office",
        }
        notes = [
            "Chip metadata extracted: DL format compliant with Sarathi portal standard.",
            "Notice: Document validity period shows expired on 2025-12-31.",
        ]
    elif hint == "SKILL_CERTIFICATE" or (not hint and any(k in fn_lower for k in ["skill", "course", "training"])):
        doc_type = "SKILL_CERTIFICATE"
        confidence = 55
        issuer = "Self-Issued / Private Vocational Institute"
        queue = VerifierQueueId.QUEUE_GENERAL
        extracted = {
            "candidate_name": "SAHIL KHUTEY",
            "course_title": "Full Stack & Cloud Architecture",
            "completion_date": "2025-11-15",
            "grade": "DISTINCTION",
        }
        notes = [
            "Unregistered issuer signature. OCR confidence moderate.",
            "Manual officer inspection required before trust elevation.",
        ]
    else:  # Fallback general document
        doc_type = "GENERAL_DOCUMENT"
        confidence = 65
        issuer = "General Issuing Authority"
        queue = VerifierQueueId.QUEUE_GENERAL
        extracted = {
            "document_title": filename,
            "ingestion_date": now.isoformat()[:10],
        }
        notes = ["General document queued for officer inspection."]


    # 1. Create UploadedDocument
    document = UploadedDocument(
        documentId=doc_id,
        ownerSubjectId=owner_id,
        documentType=doc_type,
        source="CITIZEN_UPLOAD",
        filename=filename,
        status="PENDING_VERIFICATION",
        authenticity="UNKNOWN",
        verificationLevel=2,
        currentVersion=1,
        extractedMetadata=extracted,
        createdAt=now,
    )
    DOCUMENTS[doc_id] = document
    repo.save_document(document)

    # 2. Register initial DocumentVersionRecord
    version = DocumentVersionRecord(
        versionId=f"ver_{uuid4().hex[:12]}",
        versionNumber=1,
        documentId=doc_id,
        parentVersionId=None,
        status=DocumentVersionStatus.ACTIVE,
        metadata=extracted,
        changeSummary="Citizen-uploaded document parsed via OCR classifier and queued for verifier review.",
        authority=issuer,
        createdAt=now,
    )
    VERSIONS[doc_id] = [version]
    repo.save_document_version(version)

    # 3. Create VerificationCase
    case_id = f"case_{uuid4().hex[:12]}"
    case = VerificationCase(
        caseId=case_id,
        documentId=doc_id,
        claimedIssuer=issuer,
        status="UNDER_REVIEW",
        automatedMatchScore=confidence,
        recommendedAction=f"Classified as {doc_type} ({confidence}% confidence). Enqueued for officer review.",
        verifierQueue=queue,
        createdAt=now,
    )
    CASES[case_id] = case
    repo.save_verification_case(case)

    # 4. Classification metadata result
    classification = DocumentClassificationResult(
        documentId=doc_id,
        documentType=doc_type,
        confidenceScore=confidence,
        extractedFields=extracted,
        detectedIssuer=issuer,
        suggestedQueue=queue,
        classificationNotes=notes,
        sha256=sha256_hash,
        fileSizeKb=max(12, len(content_bytes) // 100),
    )

    # 5. Build WalletDocument
    wallet_doc = WalletDocument(
        documentId=doc_id,
        title=_doc_title(doc_type, extracted),
        documentType=doc_type,
        source=DocumentSource.CITIZEN_UPLOAD,
        authenticity=AuthenticityStatus.UNKNOWN,
        validityStatus=ValidityStatus.ACTIVE,
        verificationLevel=2,
        verificationMethod=f"OCR Entity Extraction & Enqueued to {queue}",
        currentVersion=1,
        issuer=issuer,
        validUntil=None,
        extractedMetadata=extracted,
        createdAt=now,
    )
    repo.save_wallet_document(wallet_doc)

    _event("DocumentUploaded", doc_id, owner_id, f"File {filename} ingested. SHA256: {sha256_hash[:12]}...")
    _event("DocumentClassified", doc_id, owner_id, f"Classified as {doc_type} with confidence {confidence}%.")
    _event("VerificationCaseCreated", case_id, owner_id, f"Verification case enqueued into {queue}.")

    return PipelineUploadResponse(
        document=document,

        classification=classification,
        verificationCase=case,
        walletDocument=wallet_doc,
        message=f"Document successfully uploaded, classified as {doc_type} ({confidence}%), and enqueued to {queue}.",
    )




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

    # Sync metadata to active version record
    doc_versions = VERSIONS.get(document_id, [])
    if doc_versions:
        active_ver = doc_versions[-1]
        doc_versions[-1] = active_ver.model_copy(update={"metadata": metadata})

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
    queue = VerifierQueueId.QUEUE_CBSE
    if document.documentType == "LAND_RECORD":
        queue = VerifierQueueId.QUEUE_REVENUE
    elif document.documentType == "DRIVING_LICENCE":
        queue = VerifierQueueId.QUEUE_TRANSPORT
    elif document.source == "CITIZEN_UPLOAD":
        queue = VerifierQueueId.QUEUE_GENERAL

    case = VerificationCase(
        caseId=f"case_{uuid4().hex[:12]}",
        documentId=document.documentId,
        claimedIssuer=_claimed_issuer(document.documentType),
        status="UNDER_REVIEW",
        automatedMatchScore=88,
        recommendedAction="Manual verification recommended after issuer match.",
        verifierQueue=queue,
        createdAt=datetime.now(UTC),
    )
    CASES[case.caseId] = case
    updated_doc = document.model_copy(update={"status": "PENDING_VERIFICATION", "verificationLevel": 2})
    DOCUMENTS[document.documentId] = updated_doc
    _event("VerificationCaseCreated", case.caseId, document.ownerSubjectId, f"Case routed to {queue}.")
    return case


OFFICIAL_REGISTRY_MOCKS: dict[str, dict[str, Any]] = {
    "CLASS_XII": {
        "student_name": "SAHIL KHUTEY",
        "roll_number": "CBSE-2026-99214",
        "passing_year": "2026",
        "percentage": "94.2",
        "qualification": "Class XII Science",
        "institution": "Delhi Public Senior Secondary School",
        "center_code": "CTR-DEL-4019",
        "board_result": "PASS (FIRST DIVISION WITH DISTINCTION)",
    },
    "DRIVING_LICENCE": {
        "licence_number": "DL-1420210019283",
        "holder_name": "SAHIL KHUTEY",
        "vehicle_classes": "LMV, MCWG",
        "valid_till": "2025-12-31",
        "rto_jurisdiction": "DL-14 South Delhi Regional Transport Office",
        "status": "EXPIRED",
    },
    "LAND_RECORD": {
        "survey_number": "SUR-98/104",
        "khasra_no": "442/12",
        "tehsil": "Raipur Central",
        "district": "Raipur",
        "year": "1998",
        "recorded_owner": "SAHIL KHUTEY (Ancestral Title)",
        "area_hectares": "1.450",
        "land_use_type": "Agricultural / Non-Encumbered",
    },
    "SKILL_CERTIFICATE": {
        "certificate_id": "NOT_FOUND_IN_ACCREDITED_REGISTRY",
        "accreditation_status": "UNREGISTERED_ISSUER",
        "notes": "No matching record in National Skill Registry database.",
    },
}


def list_verifier_queues() -> list[VerifierQueueSummary]:
    ensure_seed_documents()
    queue_defs = [
        (VerifierQueueId.QUEUE_CBSE, "CBSE Board Verification", "Secondary & Higher Education Department"),
        (VerifierQueueId.QUEUE_REVENUE, "Land & Revenue Archives", "State Land Records & Revenue Department"),
        (VerifierQueueId.QUEUE_TRANSPORT, "Transport Authority", "Ministry of Road Transport & Highways (MoRTH)"),
        (VerifierQueueId.QUEUE_GENERAL, "General Citizen Services", "Digital Public Infrastructure Review Queue"),
    ]
    summaries: list[VerifierQueueSummary] = []
    for q_id, q_name, q_dept in queue_defs:
        q_cases = [c for c in CASES.values() if c.verifierQueue == q_id]
        pending = sum(
            1
            for c in q_cases
            if c.status in ["NEW", "OCR_COMPLETE", "ISSUER_MATCHED", "UNDER_REVIEW", "NEEDS_EVIDENCE"]
        )
        verified = sum(1 for c in q_cases if c.status == "VERIFIED")
        summaries.append(
            VerifierQueueSummary(
                queueId=q_id,
                name=q_name,
                department=q_dept,
                pendingCount=pending,
                verifiedCount=verified,
                totalCount=len(q_cases),
            )
        )
    return summaries


def list_verifier_cases(
    queue_id: VerifierQueueId | None = None,
    status: str | None = None,
) -> list[VerificationCase]:
    ensure_seed_documents()
    cases = list(CASES.values())
    if queue_id:
        cases = [c for c in cases if c.verifierQueue == queue_id]
    if status:
        cases = [c for c in cases if c.status == status]
    return sorted(cases, key=lambda c: c.createdAt, reverse=True)


def get_case_evidence_comparison(case_id: str) -> EvidenceComparisonDetail | None:
    ensure_seed_documents()
    case = CASES.get(case_id)
    if case is None:
        return None
    document = DOCUMENTS.get(case.documentId)
    if document is None:
        return None

    citizen_claims = document.extractedMetadata or {}
    official_claims = OFFICIAL_REGISTRY_MOCKS.get(document.documentType, {})

    field_comparisons: list[FieldComparison] = []
    all_keys = list(dict.fromkeys(list(citizen_claims.keys()) + list(official_claims.keys())))

    for key in all_keys:
        cit_val = str(citizen_claims.get(key, "—"))
        reg_val = str(official_claims.get(key, "—"))

        if cit_val == "—" or reg_val == "—":
            is_match = False
            conf = 40
            note = f"Attribute only available in {'citizen claim' if cit_val != '—' else 'official registry'}."
        elif cit_val.strip().upper() == reg_val.strip().upper():
            is_match = True
            conf = 100
            note = "Exact character & format match against official state records."
        else:
            is_match = False
            conf = 60
            note = f"Discrepancy detected: Citizen '{cit_val}' vs Official '{reg_val}'."

        label = key.replace("_", " ").title()
        field_comparisons.append(
            FieldComparison(
                field=key,
                label=label,
                citizenValue=cit_val,
                registryValue=reg_val,
                isMatch=is_match,
                matchConfidence=conf,
                discrepancyNote=note,
            )
        )

    return EvidenceComparisonDetail(
        caseId=case.caseId,
        documentId=document.documentId,
        documentType=document.documentType,
        subjectId=document.ownerSubjectId,
        verifierQueue=case.verifierQueue,
        claimedIssuer=case.claimedIssuer,
        overallMatchScore=case.automatedMatchScore,
        recommendedAction=case.recommendedAction,
        citizenClaims=citizen_claims,
        officialRegistryClaims=official_claims,
        fieldComparisons=field_comparisons,
        caseStatus=case.status,
        createdAt=case.createdAt,
    )


def decide_verification_case(
    case_id: str, decision: GovernmentReviewDecision
) -> VerificationCase | None:
    ensure_seed_documents()
    case = CASES.get(case_id)
    if case is None:
        return None
    now = datetime.now(UTC)

    if decision.decision == "VERIFY":
        new_status = "VERIFIED"
    elif decision.decision == "REQUEST_MORE_EVIDENCE":
        new_status = "NEEDS_EVIDENCE"
    elif decision.decision == "TRANSFER":
        new_status = "UNDER_REVIEW"
    else:  # REJECT or MARK_DUPLICATE
        new_status = "REJECTED"

    target_queue = (
        decision.transferQueue
        if (decision.decision == "TRANSFER" and decision.transferQueue)
        else case.verifierQueue
    )

    updated_case = case.model_copy(
        update={
            "status": new_status,
            "verifierQueue": target_queue,
            "decidedAt": now,
            "decision": decision,
        }
    )
    CASES[case_id] = updated_case
    repo.save_verification_case(updated_case)

    document = DOCUMENTS.get(case.documentId)
    if document is not None:
        if decision.decision == "VERIFY":
            updated_doc = document.model_copy(
                update={
                    "status": "VERIFIED",
                    "authenticity": "VERIFIED",
                    "verificationLevel": 4,
                }
            )
            DOCUMENTS[case.documentId] = updated_doc
            repo.save_document(updated_doc)

            # Mint verified Credential in database
            try:
                from app.db.session import SessionLocal
                from app.models.entities import Credential as DbCredential
                from app.models.entities import User as DbUser

                with SessionLocal() as db_session:
                    user = db_session.query(DbUser).filter(DbUser.id == document.ownerSubjectId).first()
                    if not user:
                        user = db_session.query(DbUser).first()
                    if user:
                        existing = (
                            db_session.query(DbCredential)
                            .filter(
                                DbCredential.user_id == user.id,
                                DbCredential.credential_type == document.documentType,
                            )
                            .first()
                        )
                        if not existing:
                            holder = str(
                                document.extractedMetadata.get("student_name")
                                or document.extractedMetadata.get("holder_name")
                                or "Rahul Sharma"
                            )
                            try:
                                year = int(document.extractedMetadata.get("passing_year") or 2026)
                            except (ValueError, TypeError):
                                year = 2026
                            issuer_key = "org_cbse_gov_in" if "CBSE" in case.claimedIssuer else case.claimedIssuer
                            db_session.add(
                                DbCredential(
                                    user_id=user.id,
                                    document_id=None,
                                    credential_type=document.documentType,
                                    issuer_id=issuer_key,
                                    holder_name=holder,
                                    passing_year=year,
                                    status="VERIFIED",
                                    verification_level=4,
                                )
                            )
                            db_session.commit()
            except Exception as e:
                import traceback
                print(f"[ERROR] Credential minting failed: {e}", file=sys.stderr)
                traceback.print_exc()
        elif decision.decision in ["REJECT", "MARK_DUPLICATE"]:


            updated_doc = document.model_copy(
                update={
                    "status": "REJECTED",
                    "authenticity": "REJECTED",
                }
            )
            DOCUMENTS[case.documentId] = updated_doc
            repo.save_document(updated_doc)

    event_type = (
        "VerificationCaseTransferred" if decision.decision == "TRANSFER" else "VerificationCaseDecided"
    )
    _event(
        event_type,
        case_id,
        decision.verifierId,
        f"Case {case_id} decision: {decision.decision}. Queue: {target_queue}. Note: {decision.note}",
    )
    return updated_case



def create_correction_request(
    document_id: str,
    payload: CorrectionRequestCreate,
    subject_id: str = "subj_demo_5c7b90",
) -> CorrectionRequestRecord | None:
    document = DOCUMENTS.get(document_id)
    if document is None:
        return None
    now = datetime.now(UTC)
    request = CorrectionRequestRecord(
        requestId=f"corr_{uuid4().hex[:12]}",
        documentId=document_id,
        subjectId=subject_id,
        field=payload.field,
        currentValue=payload.currentValue,
        proposedValue=payload.proposedValue,
        reason=payload.reason,
        evidenceDescription=payload.evidenceDescription,
        evidenceReference=payload.evidenceReference or f"REF-{uuid4().hex[:8].upper()}",
        status=CorrectionStatus.PENDING_REVIEW,
        createdAt=now,
    )
    CORRECTIONS[request.requestId] = request
    repo.save_correction(request)
    _event(
        "CorrectionRequested",
        request.requestId,
        subject_id,
        f"Correction request submitted for field: '{payload.field}'.",
    )
    return request


def decide_correction_request(
    request_id: str, decision: CorrectionReviewDecision
) -> CorrectionRequestRecord | None:
    request = CORRECTIONS.get(request_id)
    if request is None:
        return None
    document = DOCUMENTS.get(request.documentId)
    if document is None:
        return None
    now = datetime.now(UTC)
    if decision.decision == CorrectionDecisionType.APPROVE:
        doc_versions = VERSIONS.setdefault(document.documentId, [])
        active_ver = next((v for v in doc_versions if v.status == DocumentVersionStatus.ACTIVE), None)
        parent_id = None
        if active_ver is not None:
            idx = doc_versions.index(active_ver)
            superseded_ver = active_ver.model_copy(
                update={
                    "status": DocumentVersionStatus.SUPERSEDED,
                    "supersededAt": now,
                }
            )
            doc_versions[idx] = superseded_ver
            repo.save_document_version(superseded_ver)
            parent_id = active_ver.versionId

        new_version_num = document.currentVersion + 1
        updated_metadata = dict(document.extractedMetadata)
        if decision.correctedFields:
            updated_metadata.update(decision.correctedFields)
        else:
            updated_metadata[request.field] = request.proposedValue

        new_ver = DocumentVersionRecord(
            versionId=f"ver_{uuid4().hex[:12]}",
            versionNumber=new_version_num,
            documentId=document.documentId,
            parentVersionId=parent_id,
            status=DocumentVersionStatus.ACTIVE,
            metadata=updated_metadata,
            changeSummary=f"Correction approved: '{request.field}' updated from '{request.currentValue}' to '{request.proposedValue}'. Reason: {request.reason}",
            authority=decision.reviewerId,
            evidenceReference=request.evidenceReference,
            createdAt=now,
        )
        doc_versions.append(new_ver)
        repo.save_document_version(new_ver)

        updated_doc = document.model_copy(
            update={
                "currentVersion": new_version_num,
                "extractedMetadata": updated_metadata,
                "status": "VERIFIED",
                "authenticity": "VERIFIED",
                "verificationLevel": max(document.verificationLevel, 4),
            }
        )
        DOCUMENTS[document.documentId] = updated_doc
        repo.save_document(updated_doc)

        updated_request = request.model_copy(
            update={
                "status": CorrectionStatus.APPROVED,
                "resultingVersion": new_version_num,
                "reviewerId": decision.reviewerId,
                "reviewerNote": decision.note,
                "decidedAt": now,
            }
        )
        CORRECTIONS[request_id] = updated_request
        repo.save_correction(updated_request)
        _event(
            "CorrectionApproved",
            request_id,
            decision.reviewerId,
            f"Correction approved for '{request.field}'. Issued new version v{new_version_num}.",
        )
        _event(
            "DocumentVersionCreated",
            new_ver.versionId,
            decision.reviewerId,
            f"Document {document.documentId} version v{new_version_num} created (previous version superseded).",
        )
        return updated_request
    else:
        new_status = (
            CorrectionStatus.REJECTED
            if decision.decision == CorrectionDecisionType.REJECT
            else CorrectionStatus.MORE_INFO_REQUIRED
        )
        updated_request = request.model_copy(
            update={
                "status": new_status,
                "reviewerId": decision.reviewerId,
                "reviewerNote": decision.note,
                "decidedAt": now,
            }
        )
        CORRECTIONS[request_id] = updated_request
        repo.save_correction(updated_request)
        _event(
            "CorrectionRejected",
            request_id,
            decision.reviewerId,
            f"Correction decision: {decision.decision}. Note: {decision.note}",
        )
        return updated_request


def get_document_versions(document_id: str) -> list[DocumentVersionRecord]:

    return VERSIONS.get(document_id, [])


def list_corrections(document_id: str | None = None) -> list[CorrectionRequestRecord]:
    if document_id:
        return [c for c in CORRECTIONS.values() if c.documentId == document_id]
    return sorted(CORRECTIONS.values(), key=lambda c: c.createdAt, reverse=True)


def get_correction(request_id: str) -> CorrectionRequestRecord | None:
    return CORRECTIONS.get(request_id)



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


def _doc_title(doc_type: str, metadata: dict[str, Any]) -> str:
    if doc_type == "CLASS_XII":
        return "Secondary School Certificate (Class XII)"
    if doc_type == "DRIVING_LICENCE":
        return "Motor Driving Licence (LMV / MCWG)"
    if doc_type == "LAND_RECORD":
        return "Archival Land Title Record (Pre-Digital)"
    if doc_type == "SKILL_CERTIFICATE":
        return "Advanced Cloud & AI Engineering Certificate"
    if doc_type == "GRADUATION":
        return "Bachelor of Science Degree"
    return f"{doc_type.replace('_', ' ').title()} Record"


def _doc_issuer(doc_type: str, source: str) -> str:
    if source == "CITIZEN_UPLOAD":
        return "Self-Uploaded (Issuer Not Verified)"
    if doc_type == "CLASS_XII":
        return "Central Board of Secondary Education (CBSE)"
    if doc_type == "DRIVING_LICENCE":
        return "Ministry of Road Transport & Highways (MoRTH)"
    if doc_type == "LAND_RECORD":
        return "State Revenue & Land Records Department"
    if doc_type == "GRADUATION":
        return "State Central University"
    return "Authorised Issuing Authority"


def _doc_verification_method(level: int, source: str, status: str) -> str:
    if level == 5:
        return "Cryptographic PKI Signature & Verifiable Proof"
    if level == 4:
        return "Authorised Registry Match & Officer Audit"
    if level == 3:
        return "Issuer Registry Claim Match"
    if level == 2:
        return "Identity & Attribute Cross-Match"
    if level == 1:
        return "Automated OCR & Layout Classification"
    return "Pending Verification (Raw Citizen Upload)"

