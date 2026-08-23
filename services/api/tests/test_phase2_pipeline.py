from io import BytesIO

from fastapi.testclient import TestClient

from app.core.ids import generate_account_id
from app.db.repository import (
    get_document,
    get_document_claims,
    get_document_versions,
    get_processing_job,
    list_domain_events,
)
from app.domain.models import DocumentVersionStatus
from app.main import app
from app.services.document_pipeline import execute_processing_job, ingest_document

client = TestClient(app)


def test_phase2_document_ingestion_and_processing_e2e():
    account_id = generate_account_id()
    sample_pdf_bytes = (
        b"%PDF-1.5 Sample Document Header\n"
        b"CENTRAL BOARD OF SECONDARY EDUCATION\n"
        b"MARKS STATEMENT\n"
        b"NAME: SAHIL KHUTEY\n"
        b"ROLL: 2026-99214\n"
        b"YEAR: 2026\n"
        b"RESULT: PASS (94.2%)\n"
        b"%%EOF"
    )

    # 1. Ingestion Boundary — Immediate Return with Job ID
    res = ingest_document(
        stream=BytesIO(sample_pdf_bytes),
        filename="class_xii_marksheet.pdf",
        content_type="application/pdf",
        owner_account_id=account_id,
        document_type_hint="CLASS_XII",
    )

    assert res.status == "queued"
    assert res.document_id.startswith("doc_")
    assert res.version_id.startswith("ver_")
    assert res.processing_job_id.startswith("job_")

    # 2. Verify Relational Persistence & Object Storage Separation
    doc = get_document(res.document_id)
    assert doc is not None
    assert doc.currentVersion == 1

    versions = get_document_versions(res.document_id)
    assert len(versions) == 1
    v1 = versions[0]
    assert v1.versionId == res.version_id
    assert v1.ownerAccountId == account_id
    assert v1.objectId is not None
    assert len(v1.sha256) == 64
    assert v1.sizeBytes == len(sample_pdf_bytes)
    assert v1.status == DocumentVersionStatus.ACTIVE

    # 3. Verify Initial Job State
    job = get_processing_job(res.processing_job_id)
    assert job is not None
    assert job.status == "queued"

    # 4. Worker Processing Execution (Malware Scan -> OCR -> Claims -> Audit)
    completed_job = execute_processing_job(res.processing_job_id)
    assert completed_job.status == "completed"
    assert completed_job.malwareScan is not None
    assert completed_job.malwareScan["clean"] is True
    assert completed_job.ocrResult is not None
    assert "SAHIL KHUTEY" in completed_job.ocrResult["text"]

    # 5. Verify Extracted Claims Persistence
    claims = get_document_claims(res.document_id)
    assert len(claims) >= 1
    claim_keys = [c.claimKey for c in claims]
    assert "holder_name" in claim_keys or "passing_year" in claim_keys

    # 6. Verify Audit Trail Event Emitted
    events = list_domain_events()
    event_types = [e.type for e in events if e.aggregateId == res.document_id]
    assert "DOCUMENT_INGESTED" in event_types
    assert "DOCUMENT_OCR_PROCESSED" in event_types


def test_phase2_version_immutability_and_superseding():
    account_id = generate_account_id()
    doc_v1_bytes = b"%PDF-1.4 Version 1 Initial Document Content\n%%EOF"
    doc_v2_bytes = b"%PDF-1.4 Version 2 Corrected Document Content\n%%EOF"

    # Ingest Version 1
    v1_res = ingest_document(
        stream=BytesIO(doc_v1_bytes),
        filename="marksheet.pdf",
        content_type="application/pdf",
        owner_account_id=account_id,
    )

    # Ingest Version 2 superseding Version 1
    v2_res = ingest_document(
        stream=BytesIO(doc_v2_bytes),
        filename="marksheet_corrected.pdf",
        content_type="application/pdf",
        owner_account_id=account_id,
        parent_version_id=v1_res.version_id,
        document_id=v1_res.document_id,
    )

    versions = get_document_versions(v1_res.document_id)
    assert len(versions) == 2

    v1 = next(v for v in versions if v.versionId == v1_res.version_id)
    v2 = next(v for v in versions if v.versionId == v2_res.version_id)

    # Version 1 is marked superseded, Version 2 points to parent
    assert v1.status == DocumentVersionStatus.SUPERSEDED
    assert v1.supersededAt is not None
    assert v2.status == DocumentVersionStatus.ACTIVE
    assert v2.parentVersionId == v1.versionId
    assert v2.versionNumber == 2
    assert v1.sha256 != v2.sha256


def test_phase2_malware_detection_fails_safely():
    account_id = generate_account_id()
    malware_bytes = b"%PDF-1.4 Header with MALWARE_TEST_SIGNATURE embedded payload"

    res = ingest_document(
        stream=BytesIO(malware_bytes),
        filename="suspicious_file.pdf",
        content_type="application/pdf",
        owner_account_id=account_id,
    )

    # Process job -> should detect signature and fail safely
    job = execute_processing_job(res.processing_job_id)
    assert job.status == "failed"
    assert "Malware signature detected" in (job.errorMessage or "")

    versions = get_document_versions(res.document_id)
    v = versions[0]
    assert v.processingStatus == "malware_detected"
    assert v.status == DocumentVersionStatus.REVOKED


def test_phase2_http_multipart_ingestion_endpoint():
    pdf_content = b"%PDF-1.5 Minimal Test Document Content\n%%EOF"
    response = client.post(
        "/api/v1/documents/ingest",
        files={"file": ("student_cert.pdf", pdf_content, "application/pdf")},
        data={"document_type": "CLASS_XII", "owner_account_id": "DIN-9ABC-DEF2-3456"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert "document_id" in data
    assert "version_id" in data
    assert "processing_job_id" in data

    # Check job status endpoint
    job_res = client.get(f"/api/v1/documents/jobs/{data['processing_job_id']}")
    assert job_res.status_code == 200
    job_data = job_res.json()
    assert job_data["documentId"] == data["document_id"]
