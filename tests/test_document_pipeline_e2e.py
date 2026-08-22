"""End-to-end integration test for Document Pipeline & Government Review:
Upload ➔ OCR ➔ Case Created ➔ Officer Compares Evidence ➔ Officer Approves ➔ Credential Minted ➔ Proof Generated ➔ Proof Validated.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add services/api to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "api"))

from fastapi.testclient import TestClient
from app.main import app


def run_document_pipeline_e2e() -> None:
    client = TestClient(app)

    print(">>> 1. Health check...")
    resp = client.get("/health")
    assert resp.status_code == 200
    print("    [PASS] API is healthy")

    print(">>> 2. Citizen registers and logs in...")
    email = f"citizen_{int(time.time()*1000)}@example.com"
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123"},
    )
    assert reg_resp.status_code == 200
    auth_data = reg_resp.json()
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"    [PASS] Citizen registered: {email}")

    print(">>> 3. Citizen uploads legacy Class XII certificate...")
    upload_payload = {
        "filename": "Class_XII_CBSE_2026_Certificate.pdf",
        "documentTypeHint": "CLASS_XII",
        "simulatedContent": "CBSE Roll 26182910 Rahul Sharma Passing Year 2026",
    }
    upload_resp = client.post(
        "/api/v1/documents/upload-pipeline",
        json=upload_payload,
        headers=headers,
    )
    assert upload_resp.status_code == 200, upload_resp.text
    pipeline_data = upload_resp.json()
    doc_id = pipeline_data["document"]["documentId"]
    case_id = pipeline_data["verificationCase"]["caseId"]
    print(f"    [PASS] Document uploaded & OCR processed (Doc ID: {doc_id}, Case ID: {case_id})")
    assert pipeline_data["classification"]["confidenceScore"] >= 80

    print(">>> 4. Officer inspects review queues & evidence comparison...")
    queues_resp = client.get("/api/v1/government/queues", headers=headers)
    assert queues_resp.status_code == 200
    print("    [PASS] Departmental review queues fetched")

    comp_resp = client.get(f"/api/v1/government/cases/{case_id}/comparison", headers=headers)
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()
    assert len(comp_data["fieldComparisons"]) > 0
    print(f"    [PASS] Side-by-side evidence compared (Match Score: {comp_data['overallMatchScore']}%)")

    print(">>> 5. Government officer reviews and approves case (VERIFY)...")
    decision_payload = {
        "decision": "VERIFY",
        "verifierId": "officer_sharma_delhi_edu",
        "note": "Hologram, roll number, and state registry records match with distinction.",
    }
    dec_resp = client.post(
        f"/api/v1/government/cases/{case_id}/decision",
        json=decision_payload,
        headers=headers,
    )
    assert dec_resp.status_code == 200
    dec_data = dec_resp.json()
    assert dec_data["status"] == "VERIFIED"
    print("    [PASS] Officer approved case. Level 4 verified credential minted!")

    print(">>> 6. Check citizen wallet credentials...")
    creds_resp = client.get("/api/v1/credentials", headers=headers)
    assert creds_resp.status_code == 200
    creds = creds_resp.json()
    assert len(creds) >= 1
    verified_cred = creds[0]
    assert verified_cred["credential_type"] == "CLASS_XII"
    assert verified_cred["verification_level"] == 4
    print(f"    [PASS] Verified Credential active in wallet (ID: {verified_cred['id']})")

    print(">>> 7. Examination authority creates verification request...")
    req_resp = client.post(
        "/api/v1/verification/requests",
        json={
            "requester_name": "National Examination Authority",
            "credential_type": "CLASS_XII",
            "purpose": "Exam eligibility check",
        },
        headers=headers,
    )
    assert req_resp.status_code == 200
    req_data = req_resp.json()
    req_id = req_data["id"]
    print(f"    [PASS] Verification request created: {req_id}")

    print(">>> 8. Citizen grants consent & executes verification...")
    client.post(
        f"/api/v1/verification/requests/{req_id}/consent",
        json={"decision": "GRANT"},
        headers=headers,
    )
    run_resp = client.post(
        f"/api/v1/verification/requests/{req_id}/run",
        headers=headers,
    )
    assert run_resp.status_code == 200
    run_data = run_resp.json()
    assert run_data["result"] == "VERIFIED"
    proof_id = run_data["proof_id"]
    assert proof_id is not None
    print(f"    [PASS] Verification complete. Signed proof issued: {proof_id}")

    print(">>> 9. Validate signed proof...")
    proof_resp = client.get(f"/api/v1/proofs/{proof_id}/verify")
    assert proof_resp.status_code == 200
    assert proof_resp.json()["valid"] is True
    print("    [PASS] Cryptographic proof validated successfully!")

    print("\n=========================================================================")
    print("SUCCESS: ALL DOCUMENT PIPELINE & OFFICER REVIEW E2E STEPS PASSED (100%)")
    print("=========================================================================\n")


if __name__ == "__main__":
    run_document_pipeline_e2e()
