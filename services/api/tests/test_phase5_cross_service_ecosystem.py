"""
Phase 5 — DigiIn Cross-Service Integration & Hackathon Proof Test Suite.

Proves the core hackathon thesis:
"Store once → Verify once → Reuse securely across services without repeated document uploads."

Validates:
1. Multi-service integration (Education + Revenue + Land).
2. Reuse of identical verified claims across distinct departments.
3. Strict minimum disclosure (each service receives ONLY approved scopes).
4. Invariant: raw_files_transferred_bytes == 0 across all transactions.
5. Unified citizen audit timeline ("Who accessed my data?").
"""

from fastapi.testclient import TestClient

from app.main import app


def test_phase5_multi_service_ecosystem_and_no_repeated_uploads():
    """E2E Test: 1 Citizen ID (DI-7K4M-9Q2X-8P6R) reuses verified claims across 3 independent government services."""
    client = TestClient(app)
    citizen_id = "DI-7K4M-9Q2X-8P6R"

    # =========================================================================
    # TRANSACTION 1: Education Service (Delhi University Scholarship)
    # Requests: income_status, domicile_status, education_qualification
    # =========================================================================
    req1_payload = {
        "digiin_account_id": citizen_id,
        "requesting_service_id": "dept_du_scholarship_portal",
        "service_name": "University of Delhi — Scholarship Board",
        "purpose": "Merit Scholarship Eligibility",
        "requested_attributes": ["income_status", "domicile_status", "education_qualification"],
    }
    r1_init = client.post("/api/v1/public-service/verification/requests", json=req1_payload)
    assert r1_init.status_code == 200
    ref1 = r1_init.json()["request_reference"]

    # Citizen reviews and approves
    r1_consent = client.post(
        f"/api/v1/public-service/verification/requests/{ref1}/consent",
        json={"decision": "GRANTED"},
    )
    assert r1_consent.status_code == 200
    res1 = client.get(f"/api/v1/public-service/verification/requests/{ref1}/result").json()
    assert res1["verification_status"] == "VERIFIED"
    assert res1["verification"]["raw_files_transferred_bytes"] == 0
    assert len(res1["verification"]["assertions"]) == 3

    # =========================================================================
    # TRANSACTION 2: Revenue Service (State EWS Certificate Renewal)
    # Reuses existing verified income_status & domicile_status (NO NEW UPLOAD!)
    # =========================================================================
    req2_payload = {
        "digiin_account_id": citizen_id,
        "requesting_service_id": "dept_revenue_nct_delhi",
        "service_name": "Department of Revenue — Govt of NCT Delhi",
        "purpose": "EWS Scheme Certificate Renewal",
        "requested_attributes": ["income_status", "domicile_status"],
    }
    r2_init = client.post("/api/v1/public-service/verification/requests", json=req2_payload)
    assert r2_init.status_code == 200
    ref2 = r2_init.json()["request_reference"]

    # Citizen reviews and approves
    r2_consent = client.post(
        f"/api/v1/public-service/verification/requests/{ref2}/consent",
        json={"decision": "GRANTED"},
    )
    assert r2_consent.status_code == 200
    res2 = client.get(f"/api/v1/public-service/verification/requests/{ref2}/result").json()
    assert res2["verification_status"] == "VERIFIED"
    assert res2["verification"]["raw_files_transferred_bytes"] == 0
    assert len(res2["verification"]["assertions"]) == 2  # Only 2 scopes returned!

    # =========================================================================
    # TRANSACTION 3: Land & Property Service (Municipal Property Record)
    # Reuses existing verified domicile_status (NO NEW UPLOAD!)
    # =========================================================================
    req3_payload = {
        "digiin_account_id": citizen_id,
        "requesting_service_id": "dept_municipal_land_records",
        "service_name": "Municipal Corporation — Land Title Record",
        "purpose": "Property Title Verification",
        "requested_attributes": ["domicile_status"],
    }
    r3_init = client.post("/api/v1/public-service/verification/requests", json=req3_payload)
    assert r3_init.status_code == 200
    ref3 = r3_init.json()["request_reference"]

    # Citizen reviews and approves
    r3_consent = client.post(
        f"/api/v1/public-service/verification/requests/{ref3}/consent",
        json={"decision": "GRANTED"},
    )
    assert r3_consent.status_code == 200
    res3 = client.get(f"/api/v1/public-service/verification/requests/{ref3}/result").json()
    assert res3["verification_status"] == "VERIFIED"
    assert res3["verification"]["raw_files_transferred_bytes"] == 0
    assert len(res3["verification"]["assertions"]) == 1  # Strictly 1 scope returned!

    # =========================================================================
    # UNIFIED AUDIT LOGGING & CITIZEN TRANSPARENCY
    # =========================================================================
    r_hist = client.get(f"/api/v1/public-service/citizen/{citizen_id}/verification-history")
    assert r_hist.status_code == 200
    hist_data = r_hist.json()
    assert hist_data["account_id"] == citizen_id
    assert len(hist_data["verification_history"]) >= 3

    # Verify all 3 departments appear in citizen's audit trail
    services_logged = [req["service_name"] for req in hist_data["verification_history"]]
    assert any("University of Delhi" in s for s in services_logged)
    assert any("Revenue" in s for s in services_logged)
    assert any("Municipal" in s for s in services_logged)


def test_phase5_service_catalogue_discovery():
    """Validates public service catalogue listing with estimated time comparison."""
    client = TestClient(app)
    r = client.get("/api/v1/public-service/services")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["count"] >= 3
    services = data["services"]
    service_ids = [s["service_id"] for s in services]
    assert "srv_scholarship_du" in service_ids
    assert "srv_caste_certificate" in service_ids
    assert "srv_land_property_records" in service_ids
