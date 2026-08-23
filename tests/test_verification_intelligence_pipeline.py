"""Integration test suite for Verification Intelligence, Async Job Pipeline, Evidence Graph, and Risk Scoring."""

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


def test_verification_intelligence_and_evidence_pipeline():
    citizen_token = create_access_token(user_id="user_intel_citizen_01", role="CITIZEN")
    officer_token = create_access_token(user_id="user_intel_officer_01", role="OFFICER")

    citizen_headers = {"Authorization": f"Bearer {citizen_token}"}
    officer_headers = {"Authorization": f"Bearer {officer_token}"}

    # 1. Upload Class XII Passing Certificate
    file_bytes = b"%PDF-1.4 Mock CBSE Senior School Secondary Certificate"
    file_payload = ("class_xii_marksheet.pdf", io.BytesIO(file_bytes), "application/pdf")
    
    upload_res = client.post(
        "/api/v1/documents/upload",
        data={"document_type": "MARKSHEET", "title": "Class XII Marksheet"},
        files={"file": file_payload},
        headers=citizen_headers,
    )
    assert upload_res.status_code == 200
    doc_id = upload_res.json()["id"]

    # 2. Check Pipeline Jobs Created
    jobs_res = client.get(f"/api/v1/intelligence/documents/{doc_id}/pipeline", headers=citizen_headers)
    assert jobs_res.status_code == 200
    jobs_data = jobs_res.json()
    assert jobs_data["total_jobs"] >= 5
    job_types = [j["job_type"] for j in jobs_data["jobs"]]
    assert "MALWARE_SCAN" in job_types
    assert "OCR" in job_types
    assert "CLASSIFY" in job_types
    assert "DUPLICATE_CHECK" in job_types

    # 3. Process Verification Intelligence Pipeline
    process_res = client.post(f"/api/v1/intelligence/documents/{doc_id}/process", headers=citizen_headers)
    assert process_res.status_code == 200
    p_data = process_res.json()
    assert p_data["status"] == "VERIFICATION_READY"
    assert p_data["classification"]["type"] == "MARKSHEET"
    assert "candidate_name" in p_data["extracted_fields"]

    # 4. Inspect Extraction and Field Confidences
    ext_res = client.get(f"/api/v1/intelligence/documents/{doc_id}/extraction", headers=citizen_headers)
    assert ext_res.status_code == 200
    ext_data = ext_res.json()
    fields = ext_data["extracted_fields"]
    assert fields["candidate_name"]["confidence"] >= 0.90
    assert fields["document_number"]["confidence"] >= 0.90

    # 5. Inspect Verification Evidence Graph
    ev_res = client.get(f"/api/v1/intelligence/documents/{doc_id}/evidence", headers=citizen_headers)
    assert ev_res.status_code == 200
    ev_data = ev_res.json()
    assert ev_data["evidence_count"] >= 3
    ev_types = [e["evidence_type"] for e in ev_data["evidence"]]
    assert "DOCUMENT" in ev_types
    assert "OCR" in ev_types
    assert "QR_CODE" in ev_types

    # 6. Inspect Multi-Factor Risk Assessment
    risk_res = client.get(f"/api/v1/intelligence/documents/{doc_id}/risk", headers=citizen_headers)
    assert risk_res.status_code == 200
    risk_data = risk_res.json()
    assert risk_data["score"] >= 70
    assert risk_data["level"] in ["LOW_RISK", "NORMAL"]

    # 7. Officer Reviews and Approves with Evidence
    decision_res = client.post(
        f"/api/v1/review/documents/{doc_id}/decision",
        json={"decision": "APPROVE", "reason": "All evidence signals verified against CBSE registry."},
        headers=officer_headers,
    )
    assert decision_res.status_code == 200
    assert decision_res.json()["status"] == "VERIFIED"


if __name__ == "__main__":
    test_verification_intelligence_and_evidence_pipeline()
    print("SUCCESS: ALL VERIFICATION INTELLIGENCE AND EVIDENCE PIPELINE TESTS PASSED!")
