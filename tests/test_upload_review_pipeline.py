"""End-to-end integration test suite for Document Upload, Versioning, and Government Officer Review Lifecycle."""

from __future__ import annotations

import io
import sys
from pathlib import Path

# Add services and repo root to sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "services" / "api"))
sys.path.insert(0, str(root_dir))

from fastapi.testclient import TestClient
from app.core.security import create_access_token
from app.db.session import init_db
from app.main import app

init_db()
client = TestClient(app)


def test_document_upload_and_government_review_lifecycle():
    # 1. Setup authenticated citizen & officer tokens
    citizen_user_id = "user_citizen_upload_test_01"
    officer_user_id = "user_officer_review_test_01"

    citizen_token = create_access_token(user_id=citizen_user_id, role="CITIZEN")
    officer_token = create_access_token(user_id=officer_user_id, role="OFFICER")

    citizen_headers = {"Authorization": f"Bearer {citizen_token}"}
    officer_headers = {"Authorization": f"Bearer {officer_token}"}

    # 2. Upload Document as Citizen
    file_bytes = b"%PDF-1.4 Mock Senior School Secondary Certificate Document Bytes"
    file_payload = ("class_xii_certificate.pdf", io.BytesIO(file_bytes), "application/pdf")
    
    upload_res = client.post(
        "/api/v1/documents/upload",
        data={"document_type": "CLASS_XII", "title": "Class XII Passing Certificate"},
        files={"file": file_payload},
        headers=citizen_headers,
    )
    assert upload_res.status_code == 200, upload_res.text
    upload_data = upload_res.json()
    doc_id = upload_data["id"]
    assert upload_data["status"] == "PENDING_REVIEW"
    assert len(upload_data["sha256"]) == 64
    assert upload_data["filename"] == "class_xii_certificate.pdf"

    # 3. List Documents for Citizen
    list_res = client.get("/api/v1/documents", headers=citizen_headers)
    assert list_res.status_code == 200
    docs = list_res.json()
    assert any(d["id"] == doc_id for d in docs)

    # 4. Get Document Detail & Versions for Citizen
    detail_res = client.get(f"/api/v1/documents/{doc_id}", headers=citizen_headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["document"]["id"] == doc_id
    assert len(detail_data["versions"]) >= 1
    assert detail_data["versions"][0]["version"] == 1
    assert detail_data["versions"][0]["sha256"] == upload_data["sha256"]

    # 5. Government Officer Inspects Review Queue
    queue_res = client.get("/api/v1/review/documents", headers=officer_headers)
    assert queue_res.status_code == 200
    queue_docs = queue_res.json()
    assert any(d["id"] == doc_id for d in queue_docs)

    # 6. Officer Inspects Document Detail
    officer_detail_res = client.get(f"/api/v1/review/documents/{doc_id}", headers=officer_headers)
    assert officer_detail_res.status_code == 200
    assert officer_detail_res.json()["document"]["id"] == doc_id

    # 7. Citizen Requests Record Correction
    corr_res = client.post(
        f"/api/v1/documents/{doc_id}/request-correction",
        data={"issue_type": "TYPO_IN_NAME", "description": "Candidate name spelling correction."},
        headers=citizen_headers,
    )
    assert corr_res.status_code == 200
    assert corr_res.json()["document_status"] == "CORRECTION_REQUIRED"

    # 8. Officer Approves Document (Mints Level 3/4 Verified Credential)
    decision_res = client.post(
        f"/api/v1/review/documents/{doc_id}/decision",
        json={"decision": "APPROVE", "reason": "Verified against CBSE government registry records."},
        headers=officer_headers,
    )
    assert decision_res.status_code == 200
    assert decision_res.json()["status"] == "VERIFIED"

    # 9. Verify Citizen Credentials received new Verified Credential
    creds_res = client.get("/api/v1/credentials", headers=citizen_headers)
    assert creds_res.status_code == 200


def test_invalid_file_type_and_size_validation():
    citizen_token = create_access_token(user_id="user_validation_test_01", role="CITIZEN")
    citizen_headers = {"Authorization": f"Bearer {citizen_token}"}

    # 1. Unsupported MIME type
    invalid_file = ("script.exe", io.BytesIO(b"MZ executable bytes"), "application/x-msdownload")
    bad_type_res = client.post(
        "/api/v1/documents/upload",
        data={"document_type": "CLASS_XII", "title": "Malicious Payload"},
        files={"file": invalid_file},
        headers=citizen_headers,
    )
    assert bad_type_res.status_code == 415

    # 2. Empty file
    empty_file = ("empty.pdf", io.BytesIO(b""), "application/pdf")
    empty_res = client.post(
        "/api/v1/documents/upload",
        data={"document_type": "CLASS_XII", "title": "Empty Document"},
        files={"file": empty_file},
        headers=citizen_headers,
    )
    assert empty_res.status_code == 400


if __name__ == "__main__":
    test_document_upload_and_government_review_lifecycle()
    test_invalid_file_type_and_size_validation()
    print("SUCCESS: ALL DOCUMENT UPLOAD AND GOVERNMENT REVIEW LIFECYCLE TESTS PASSED!")
