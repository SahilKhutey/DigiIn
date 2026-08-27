"""
Phase 3 — DigiIn Verification Infrastructure Test Suite.

Validates:
1. Formal Verification Request Creation (VR-XXXXXX).
2. Minimum disclosure scope filtering (0 raw file bytes transferred).
3. Citizen Consent Workflow (Approval, Denial, Revocation).
4. Request TTL Expiration (10-minute limit).
5. Transparency Audit Trail ("Who accessed my DigiIn information?").
6. Separation of Attribute Verification from Document Vault downloads.
"""

import time

from fastapi.testclient import TestClient

from app.main import app


def test_phase3_verification_request_creation_and_inspection():
    """Validates creation of verification request with 10-minute expiry."""
    client = TestClient(app)
    payload = {
        "digiin_account_id": "DI-7K4M-9Q2X-8P6R",
        "requesting_service_id": "dept_du_scholarship_portal",
        "service_name": "University of Delhi — Scholarship Board",
        "purpose": "Merit-cum-Means Scholarship Evaluation",
        "requested_attributes": ["income_status", "domicile_status", "education_qualification"],
        "ttl_seconds": 600,
    }

    # 1. Create request
    r = client.post("/api/v1/public-service/verification/requests", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    req_ref = data["request_reference"]
    assert req_ref.startswith("VR-")
    assert data["verification_status"] == "consent_required"

    # 2. Inspect request
    r_get = client.get(f"/api/v1/public-service/verification/requests/{req_ref}")
    assert r_get.status_code == 200
    inspect_data = r_get.json()["request"]
    assert inspect_data["status"] == "PENDING_CONSENT"
    assert inspect_data["purpose"] == "Merit-cum-Means Scholarship Evaluation"
    assert len(inspect_data["requested_attributes"]) == 3


def test_phase3_citizen_consent_approval_and_minimum_disclosure():
    """Validates citizen granting consent, triggering verification engine with 0 raw bytes."""
    client = TestClient(app)
    # Create request
    payload = {
        "digiin_account_id": "DI-7K4M-9Q2X-8P6R",
        "requesting_service_id": "dept_du_scholarship_portal",
        "service_name": "University of Delhi",
        "purpose": "Scholarship Evaluation",
        "requested_attributes": ["income_status", "education_qualification"],
    }
    r = client.post("/api/v1/public-service/verification/requests", json=payload)
    req_ref = r.json()["request_reference"]

    # Citizen approves
    r_consent = client.post(
        f"/api/v1/public-service/verification/requests/{req_ref}/consent",
        json={"decision": "GRANTED"},
    )
    assert r_consent.status_code == 200
    consent_data = r_consent.json()
    assert consent_data["verification_status"] == "VERIFIED"
    assert consent_data["consent_status"] == "GRANTED"

    # Verifier retrieves result
    r_res = client.get(f"/api/v1/public-service/verification/requests/{req_ref}/result")
    assert r_res.status_code == 200
    res_data = r_res.json()
    assert res_data["verification_status"] == "VERIFIED"
    assertions = res_data["verification"]["assertions"]
    assert len(assertions) == 2
    assert res_data["verification"]["raw_files_transferred_bytes"] == 0  # Invariant: Zero raw bytes

    # Check that assertions contain issuing authority and status
    attr_names = [a["attribute"] for a in assertions]
    assert "income_status" in attr_names
    assert "education_qualification" in attr_names
    for a in assertions:
        assert a["status"] == "VERIFIED"
        assert len(a["issuing_authority"]) > 0


def test_phase3_citizen_consent_denial():
    """Validates citizen denying consent, resulting in ACCESS_DENIED with no data disclosed."""
    client = TestClient(app)
    payload = {
        "digiin_account_id": "DI-7K4M-9Q2X-8P6R",
        "requesting_service_id": "dept_unknown_service",
        "service_name": "Third Party Portal",
        "purpose": "General Inquiry",
        "requested_attributes": ["income_status"],
    }
    r = client.post("/api/v1/public-service/verification/requests", json=payload)
    req_ref = r.json()["request_reference"]

    # Citizen denies
    r_deny = client.post(
        f"/api/v1/public-service/verification/requests/{req_ref}/consent",
        json={"decision": "DENIED"},
    )
    assert r_deny.status_code == 200
    deny_data = r_deny.json()
    assert deny_data["verification_status"] == "DENIED"
    assert deny_data["consent_status"] == "DENIED"
    assert deny_data["result"]["verification_status"] == "ACCESS_DENIED"
    assert len(deny_data["result"]["assertions"]) == 0


def test_phase3_consent_revocation():
    """Validates citizen unilaterally revoking access after granting it."""
    client = TestClient(app)
    payload = {
        "digiin_account_id": "DI-7K4M-9Q2X-8P6R",
        "requesting_service_id": "dept_du_scholarship_portal",
        "service_name": "Delhi University",
        "purpose": "Revocation Test",
        "requested_attributes": ["domicile_status"],
    }
    r = client.post("/api/v1/public-service/verification/requests", json=payload)
    req_ref = r.json()["request_reference"]

    # Approve first
    client.post(
        f"/api/v1/public-service/verification/requests/{req_ref}/consent",
        json={"decision": "GRANTED"},
    )

    # Now citizen revokes
    r_revoke = client.post(f"/api/v1/public-service/verification/requests/{req_ref}/revoke")
    assert r_revoke.status_code == 200
    assert r_revoke.json()["consent_status"] == "REVOKED"
    assert r_revoke.json()["verification_status"] == "REVOKED"


def test_phase3_request_expiration():
    """Validates that expired verification requests (past TTL) reject consent."""
    client = TestClient(app)
    payload = {
        "digiin_account_id": "DI-7K4M-9Q2X-8P6R",
        "requesting_service_id": "dept_test",
        "service_name": "Test Service",
        "purpose": "Expiration Test",
        "requested_attributes": ["income_status"],
        "ttl_seconds": 1,  # 1 second TTL
    }
    r = client.post("/api/v1/public-service/verification/requests", json=payload)
    req_ref = r.json()["request_reference"]

    # Wait for TTL expiry
    time.sleep(1.2)

    # Attempting to grant consent on expired request must fail with 400
    r_exp = client.post(
        f"/api/v1/public-service/verification/requests/{req_ref}/consent",
        json={"decision": "GRANTED"},
    )
    assert r_exp.status_code == 400
    assert "expired" in r_exp.json()["detail"].lower()


def test_phase3_citizen_transparency_history():
    """Validates citizen transparency audit view ('Who accessed my DigiIn information?')."""
    client = TestClient(app)
    r = client.get("/api/v1/public-service/citizen/DI-7K4M-9Q2X-8P6R/verification-history")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["account_id"] == "DI-7K4M-9Q2X-8P6R"
    assert "verification_history" in data
    assert "audit_trail" in data
    assert len(data["verification_history"]) >= 1
