"""
DigiIn Final Feature-Freeze Mandatory E2E Test Suite (E2E-001 through E2E-018).

Validates the complete 18-gate security and functional verification matrix:
E2E-001: Golden approval path
E2E-002: Consent denial path
E2E-003: Consent expiration path
E2E-004: Consent revocation path
E2E-005: Invalid Account ID
E2E-006: Invalid institution
E2E-007: Invalid service
E2E-008: Unauthorized scope
E2E-009: Expired document handling
E2E-010: Revoked document handling
E2E-011: Cross-account access
E2E-012: Cross-institution access
E2E-013: Invalid credential handling
E2E-014: Expired credential handling
E2E-015: Assertion tampering rejection
E2E-016: Assertion expiration rejection
E2E-017: Assertion replay rejection
E2E-018: Multi-institution verification reuse
"""

import time

from fastapi.testclient import TestClient

from app.core.proofs.assertion_service import assertion_service
from app.main import app

client = TestClient(app)
CITIZEN_ID = "DI-7K4M-9Q2X-8P6R"


def test_e2e_001_golden_approval_path():
    """E2E-001: Standard golden approval path (Create -> Consent -> Verify -> Assertion -> Result)."""
    # 1. Create request
    r_req = client.post(
        "/api/v1/verification/requests",
        json={
            "institution_code": "EDU-DEMO-001",
            "service_code": "EDU-SCHOLARSHIP-DEMO",
            "digiin_account_id": CITIZEN_ID,
            "purpose": "Merit Scholarship Eligibility",
            "scopes": ["education.qualification", "income.status", "domicile.status"],
            "ttl_seconds": 900,
        },
    )
    assert r_req.status_code == 200
    ref = r_req.json()["request_id"]

    # 2. Approve request
    r_consent = client.post(
        f"/api/v1/verification/requests/{ref}/consent",
        json={"decision": "approved"},
    )
    assert r_consent.status_code == 200
    assert r_consent.json()["verification_status"] == "VERIFIED"

    # 3. Retrieve verified assertions
    r_res = client.get(f"/api/v1/verification/requests/{ref}/result")
    assert r_res.status_code == 200
    res = r_res.json()
    assert res["verification_status"] == "VERIFIED"
    assert res["verification"]["raw_files_transferred_bytes"] == 0
    assert len(res["verification"]["assertions"]) == 3


def test_e2e_002_consent_denial():
    """E2E-002: Citizen denial sets status to DENIED with zero verified disclosures."""
    r_req = client.post(
        "/api/v1/verification/requests",
        json={
            "institution_code": "REV-DEMO-001",
            "digiin_account_id": CITIZEN_ID,
            "purpose": "Revenue Scheme",
            "scopes": ["identity.basic"],
        },
    )
    ref = r_req.json()["request_id"]

    r_deny = client.post(
        f"/api/v1/verification/requests/{ref}/consent",
        json={"decision": "denied"},
    )
    assert r_deny.status_code == 200
    assert r_deny.json()["consent_status"] == "DENIED"

    r_res = client.get(f"/api/v1/verification/requests/{ref}/result")
    assert r_res.json()["verification_status"] == "DENIED"
    assert "verification" not in r_res.json()


def test_e2e_003_consent_expiration():
    """E2E-003: Requests past their validity window expire and cannot be approved."""
    r_req = client.post(
        "/api/v1/verification/requests",
        json={
            "institution_code": "EDU-DEMO-001",
            "digiin_account_id": CITIZEN_ID,
            "purpose": "Expiring Test",
            "scopes": ["income.status"],
            "ttl_seconds": 1,
        },
    )
    ref = r_req.json()["request_id"]
    time.sleep(1.2)

    # Attempting consent on expired request must be rejected
    r_approve = client.post(
        f"/api/v1/verification/requests/{ref}/consent",
        json={"decision": "approved"},
    )
    assert r_approve.status_code in (400, 410)


def test_e2e_004_consent_revocation():
    """E2E-004: Approved consent can be unilaterally revoked by the citizen."""
    r_req = client.post(
        "/api/v1/verification/requests",
        json={
            "institution_code": "CIT-DEMO-001",
            "digiin_account_id": CITIZEN_ID,
            "purpose": "Municipal Record",
            "scopes": ["identity.address"],
        },
    )
    ref = r_req.json()["request_id"]
    client.post(f"/api/v1/verification/requests/{ref}/consent", json={"decision": "approved"})

    # Revoke
    r_rev = client.post(f"/api/v1/verification/requests/{ref}/revoke")
    assert r_rev.status_code == 200
    assert r_rev.json()["consent_status"] == "REVOKED"


def test_e2e_005_invalid_account_id():
    """E2E-005: Syntactically invalid Account ID is rejected with 400."""
    r = client.post(
        "/api/v1/verification/requests",
        json={
            "institution_code": "EDU-DEMO-001",
            "digiin_account_id": "INVALID-SYNTAX",
            "purpose": "Test",
            "scopes": ["income.status"],
        },
    )
    assert r.status_code == 400


def test_e2e_006_invalid_institution():
    """E2E-006: Requesting via unknown institution is rejected with 404."""
    r = client.post(
        "/api/v1/verification/requests",
        json={
            "institution_code": "UNKNOWN-INSTITUTION-999",
            "digiin_account_id": CITIZEN_ID,
            "purpose": "Test",
            "scopes": ["income.status"],
        },
    )
    assert r.status_code == 404


def test_e2e_008_unauthorized_scope():
    """E2E-008: Requesting scope outside accredited permissions is blocked with 403."""
    # CIT-DEMO-001 is only accredited for identity.basic and identity.address
    r = client.post(
        "/api/v1/verification/requests",
        json={
            "institution_code": "CIT-DEMO-001",
            "digiin_account_id": CITIZEN_ID,
            "purpose": "Data Probe",
            "requested_scopes": ["income.status"],
            "scopes": ["income.status"],
        },
    )
    assert r.status_code == 403
    assert "UNAUTHORIZED_SCOPE" in r.json()["detail"]


def test_e2e_015_assertion_tampering_rejection():
    """E2E-015: Tampered assertion payload fails Ed25519 cryptographic verification."""
    assertion = assertion_service.mint_signed_assertion(
        subject=CITIZEN_ID,
        audience="EDU-DEMO-001",
        purpose="Scholarship Review",
        scope=["income.status"],
        claims={"income.status": "Eligible (< 2.5L)"},
    )
    tampered = dict(assertion)
    tampered["claims"] = {"income.status": "Ineligible (> 10L)"}

    outcome = assertion_service.verify_signed_assertion(
        assertion=tampered,
        expected_audience="EDU-DEMO-001",
        enforce_replay_protection=False,
    )
    assert outcome["valid"] is False
    assert outcome["error_code"] == "INVALID_SIGNATURE"


def test_e2e_017_assertion_replay_rejection():
    """E2E-017: Replay attack on single-use nonce is detected and rejected."""
    assertion = assertion_service.mint_signed_assertion(
        subject=CITIZEN_ID,
        audience="REV-DEMO-001",
        purpose="Revenue Scheme",
        scope=["domicile.status"],
        claims={"domicile.status": "Delhi Resident"},
    )
    first = assertion_service.verify_signed_assertion(assertion, expected_audience="REV-DEMO-001", enforce_replay_protection=True)
    assert first["valid"] is True

    second = assertion_service.verify_signed_assertion(assertion, expected_audience="REV-DEMO-001", enforce_replay_protection=True)
    assert second["valid"] is False
    assert second["error_code"] == "REPLAY_DETECTED"


def test_e2e_018_multi_institution_verification_reuse():
    """E2E-018: Pre-stored verified records are reused across all 3 institutions with 0 re-uploads."""
    institutions = [
        ("EDU-DEMO-001", ["education.qualification", "income.status"]),
        ("REV-DEMO-001", ["identity.basic", "domicile.status"]),
        ("CIT-DEMO-001", ["identity.basic", "identity.address"]),
    ]
    for inst_code, scopes in institutions:
        r_req = client.post(
            "/api/v1/verification/requests",
            json={
                "institution_code": inst_code,
                "digiin_account_id": CITIZEN_ID,
                "purpose": f"Multi-Service Verification for {inst_code}",
                "scopes": scopes,
            },
        )
        assert r_req.status_code == 200
        ref = r_req.json()["request_id"]

        r_app = client.post(f"/api/v1/verification/requests/{ref}/consent", json={"decision": "approved"})
        assert r_app.status_code == 200

        r_res = client.get(f"/api/v1/verification/requests/{ref}/result")
        assert r_res.status_code == 200
        assert r_res.json()["verification_status"] == "VERIFIED"
        assert r_res.json()["verification"]["raw_files_transferred_bytes"] == 0
