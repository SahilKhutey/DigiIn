"""End-to-end verification lifecycle integration test.

Tests the full vertical slice:
1. Verifier creates a verification request (NTA requesting Class XII).
2. Citizen fetches the pending verification request.
3. Citizen authorizes consent with selective attribute disclosure.
4. DigiLocker X evaluates claims against authoritative mock issuer.
5. Signed Ed25519 proof token is issued and returned.
6. Requester introspects and validates the proof token.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add services/api to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "api"))

from fastapi.testclient import TestClient
from app.main import app


def run_e2e_verification_flow() -> None:
    client = TestClient(app)

    print(">>> 1. Health check...")
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    print("    [PASS] API is operational")

    print(">>> 2. Verifier issues verification request...")
    req_payload = {
        "clientId": "client_nta_exam_portal",
        "requesterName": "National Testing Agency",
        "purpose": "Joint Entrance Examination (JEE) Application Verification",
        "audience": "aud_nta_portal",
        "requirements": [
            {
                "credential": "CLASS_XII",
                "required": True,
                "minimumLevel": 3,
                "attributes": ["qualification", "passing_year"],
            }
        ],
        "disclosure": {
            "mode": "ATTRIBUTE",
            "attributes": ["qualification", "passing_year"],
        },
        "ttlMinutes": 15,
    }
    resp = client.post("/api/v1/verification/request", json=req_payload)
    assert resp.status_code == 200, resp.text
    req_data = resp.json()
    request_id = req_data["requestId"]
    print(f"    [PASS] Verification request created: {request_id}")

    print(">>> 3. Citizen reviews pending request...")
    resp = client.get(f"/api/v1/verification/request/{request_id}")
    assert resp.status_code == 200
    assert resp.json()["requesterName"] == "National Testing Agency"
    print("    [PASS] Request retrieved by citizen wallet")

    print(">>> 4. Citizen authorizes consent with selective disclosure...")
    auth_payload = {
        "allow": True,
        "subjectId": "subj_demo_5c7b90",
        "customDisclosure": {
            "mode": "SELECTIVE_ATTRIBUTES",
            "selectedAttributes": ["qualification", "passing_year"],
            "selectedPredicates": [],
        },
    }
    resp = client.post(f"/api/v1/verification/request/{request_id}/authorize", json=auth_payload)
    assert resp.status_code == 200, resp.text
    result_data = resp.json()
    assert result_data["status"] == "VERIFIED"
    assert "proof" in result_data
    token = result_data["proof"]["token"]
    print(f"    [PASS] Consent granted & signed proof generated (Verification ID: {result_data['verificationId']})")

    print(">>> 5. Requester introspects and validates signed proof token...")
    introspect_payload = {
        "token": token,
        "audience": "aud_nta_portal",
    }
    resp = client.post("/api/v1/verification/introspect", json=introspect_payload)
    assert resp.status_code == 200, resp.text
    intro_data = resp.json()
    assert intro_data["active"] is True
    assert intro_data["status"] == "TRUSTED_PROOF"
    assert intro_data["cryptoVerified"] is True
    print("    [PASS] Proof token successfully introspected and cryptographically validated!")

    print("\n=======================================================")
    print("SUCCESS: ALL END-TO-END VERIFICATION FLOW STEPS PASSED")
    print("=======================================================\n")


if __name__ == "__main__":
    run_e2e_verification_flow()
