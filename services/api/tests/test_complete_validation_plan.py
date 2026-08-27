"""
DigiIn Complete Test, Verification & Validation Test Suite.
Covers the comprehensive verification chain aligned with OWASP ASVS & NIST SP 800-63-4:

Trust Chain:
DigiIn Account ID → Institution → Service → Verification Request → Scope
→ Consent → Verification → Assertion → Result → Audit → Revocation/Expiry
"""

import pytest
from fastapi.testclient import TestClient

from app.core.ids import generate_account_id, is_valid_account_id
from app.core.proofs.assertion_service import assertion_service
from app.main import app

client = TestClient(app)


# =============================================================================
# PHASE A — ACCOUNT ID TESTS (ID-001 to ID-006)
# =============================================================================

def test_id_001_generation_and_format():
    """ID-001: Valid unique DigiIn Account ID generation matching DI-XXXX-XXXX-XXXX."""
    account_id = generate_account_id()
    assert is_valid_account_id(account_id)
    assert account_id.startswith("DI-")
    assert len(account_id) == 17
    # Base32 alphabet exclusion check (no 0, 1, I, O)
    assert not any(c in "01IO" for c in account_id.replace("DI-", "").replace("-", ""))


def test_id_002_uniqueness_bulk():
    """ID-002: Generation of 2,000 IDs with zero collisions."""
    ids = {generate_account_id() for _ in range(2000)}
    assert len(ids) == 2000


def test_id_004_enumeration_resistance_and_invalid_id():
    """ID-004 & ID-005 & ID-006: Invalid and nonexistent ID probing returns non-disclosing 404/400."""
    # Invalid syntactic ID
    r_invalid = client.get("/api/v1/accounts/INVALID-FORMAT")
    assert r_invalid.status_code == 400

    # Syntactically valid but nonexistent ID
    r_nonexistent = client.get("/api/v1/accounts/DI-9999-9999-9999")
    assert r_nonexistent.status_code == 404
    assert "account_not_found" in r_nonexistent.json()["detail"].lower()


# =============================================================================
# PHASE B & C — INSTITUTION & SERVICE REGISTRATION TESTS (INS-001 to SRV-003)
# =============================================================================

def test_ins_001_institution_status_and_environment():
    """INS-001: Registered institutions are tagged ACTIVE and SANDBOX."""
    r = client.get("/api/v1/public-service/sandbox/institutions")
    assert r.status_code == 200
    institutions = r.json()["institutions"]
    for inst in institutions:
        assert inst["status"] == "ACTIVE"
        assert inst["environment"] == "SANDBOX"


def test_ins_003_unknown_institution_rejected():
    """INS-003: Nonexistent institution request is rejected with 404."""
    payload = {
        "institution_code": "UNKNOWN-DEMO-999",
        "account_id": "DI-7K4M-9Q2X-8P6R",
        "purpose": "Test",
        "requested_scopes": ["identity.basic"],
    }
    r = client.post("/api/v1/public-service/sandbox/verification-requests", json=payload)
    assert r.status_code == 404


# =============================================================================
# PHASE D — SCOPE ACCREDITATION TESTS (SCP-001 to SCP-004)
# =============================================================================

def test_scp_002_unauthorized_scope_rejected():
    """SCP-002: Requesting scopes outside institution accreditation is strictly blocked with 403."""
    # CIT-DEMO-001 is only accredited for identity.basic and identity.address
    payload = {
        "institution_code": "CIT-DEMO-001",
        "account_id": "DI-7K4M-9Q2X-8P6R",
        "purpose": "Unauthorized Income Probing",
        "requested_scopes": ["identity.basic", "income.status"],
    }
    r = client.post("/api/v1/public-service/sandbox/verification-requests", json=payload)
    assert r.status_code == 403
    assert "UNAUTHORIZED_SCOPE" in r.json()["detail"]


# =============================================================================
# PHASE F & G & H — VERIFICATION, CONSENT & ENGINE TESTS (VR-001 to VER-006)
# =============================================================================

def test_con_005_consent_denial_workflow():
    """CON-005: Citizen denial sets status to DENIED with 0 verified disclosures."""
    # 1. Dispatch request
    req_payload = {
        "institution_code": "EDU-DEMO-001",
        "account_id": "DI-7K4M-9Q2X-8P6R",
        "purpose": "Scholarship Review",
        "requested_scopes": ["education.qualification", "income.status"],
    }
    r_req = client.post("/api/v1/public-service/sandbox/verification-requests", json=req_payload)
    assert r_req.status_code == 200
    ref = r_req.json()["verification_request"]["request_reference"]

    # 2. Citizen explicitly denies
    r_deny = client.post(
        f"/api/v1/public-service/verification/requests/{ref}/consent",
        json={"decision": "DENIED"},
    )
    assert r_deny.status_code == 200
    res_deny = r_deny.json()
    assert res_deny["consent_status"] == "DENIED"
    assert res_deny["verification_status"] == "DENIED"

    # 3. Result polling returns pending/denied without verified claims
    r_res = client.get(f"/api/v1/public-service/verification/requests/{ref}/result")
    assert r_res.json()["verification_status"] == "DENIED"
    assert "assertions" not in r_res.json()


def test_con_009_consent_revocation():
    """CON-009: Citizen can unilaterally revoke an approved verification."""
    # 1. Create and approve request
    req_payload = {
        "institution_code": "REV-DEMO-001",
        "account_id": "DI-7K4M-9Q2X-8P6R",
        "purpose": "Revenue Scheme",
        "requested_scopes": ["identity.basic", "domicile.status"],
    }
    r_req = client.post("/api/v1/public-service/sandbox/verification-requests", json=req_payload)
    ref = r_req.json()["verification_request"]["request_reference"]

    client.post(
        f"/api/v1/public-service/verification/requests/{ref}/consent",
        json={"decision": "GRANTED"},
    )

    # 2. Citizen revokes consent
    r_revoke = client.post(f"/api/v1/public-service/verification/requests/{ref}/revoke")
    assert r_revoke.status_code == 200
    res_revoke = r_revoke.json()
    assert res_revoke["consent_status"] == "REVOKED"
    assert res_revoke["verification_status"] == "REVOKED"


# =============================================================================
# PHASE I & J — ASSERTION CRYPTOGRAPHY & DATA MINIMIZATION (AST-001 to AST-007)
# =============================================================================

def test_ast_005_cryptographic_tamper_detection():
    """AST-005: Tampering with signed assertion payload invalidates Ed25519 signature."""
    assertion = assertion_service.mint_signed_assertion(
        subject="DI-7K4M-9Q2X-8P6R",
        audience="EDU-DEMO-001",
        purpose="Scholarship Review",
        scope=["income.status"],
        claims={"income.status": "Eligible (< 2.5L)"},
    )

    # Tamper with the claims
    tampered = dict(assertion)
    tampered["claims"] = {"income.status": "Ineligible (> 10L)"}

    outcome = assertion_service.verify_signed_assertion(
        assertion=tampered,
        expected_audience="EDU-DEMO-001",
        enforce_replay_protection=False,
    )
    assert outcome["valid"] is False
    assert outcome["error_code"] == "INVALID_SIGNATURE"


def test_ast_007_replay_protection():
    """AST-007: Presenting identical nonce assertion twice triggers REPLAY_DETECTED."""
    assertion = assertion_service.mint_signed_assertion(
        subject="DI-7K4M-9Q2X-8P6R",
        audience="EDU-DEMO-001",
        purpose="Scholarship Review",
        scope=["domicile.status"],
        claims={"domicile.status": "Delhi Resident"},
    )

    # First presentation passes
    first = assertion_service.verify_signed_assertion(
        assertion=assertion,
        expected_audience="EDU-DEMO-001",
        enforce_replay_protection=True,
    )
    assert first["valid"] is True

    # Immediate second presentation fails
    second = assertion_service.verify_signed_assertion(
        assertion=assertion,
        expected_audience="EDU-DEMO-001",
        enforce_replay_protection=True,
    )
    assert second["valid"] is False
    assert second["error_code"] == "REPLAY_DETECTED"


def test_data_minimization_zero_raw_files_transferred():
    """Phase J: Strict data minimization ensures raw_files_transferred_bytes == 0."""
    req_payload = {
        "institution_code": "EDU-DEMO-001",
        "account_id": "DI-7K4M-9Q2X-8P6R",
        "purpose": "Scholarship Review",
        "requested_scopes": ["education.qualification", "income.status", "domicile.status"],
    }
    r_req = client.post("/api/v1/public-service/sandbox/verification-requests", json=req_payload)
    ref = r_req.json()["verification_request"]["request_reference"]

    client.post(
        f"/api/v1/public-service/verification/requests/{ref}/consent",
        json={"decision": "GRANTED"},
    )

    res = client.get(f"/api/v1/public-service/verification/requests/{ref}/result").json()
    assert res["verification_status"] == "VERIFIED"
    assert res["verification"]["raw_files_transferred_bytes"] == 0
    assert "pdf" not in str(res).lower()


# =============================================================================
# PHASE N — PARAMETERIZED MULTI-INSTITUTION GOLDEN PATH (E2E-001 & E2E-002)
# =============================================================================

@pytest.mark.parametrize(
    "inst_code, scopes",
    [
        ("EDU-DEMO-001", ["education.qualification", "income.status", "domicile.status"]),
        ("REV-DEMO-001", ["identity.basic", "identity.address", "domicile.status"]),
        ("CIT-DEMO-001", ["identity.basic", "identity.address"]),
    ],
)
def test_e2e_002_multi_institution_golden_path(inst_code: str, scopes: list[str]):
    """E2E-002: Proves the complete multi-institution golden path across all 3 sandbox institutions."""
    citizen_id = "DI-7K4M-9Q2X-8P6R"

    # Step 1: Institution creates verification request
    r_req = client.post(
        "/api/v1/public-service/sandbox/verification-requests",
        json={
            "institution_code": inst_code,
            "account_id": citizen_id,
            "purpose": f"E2E Automated Verification for {inst_code}",
            "requested_scopes": scopes,
            "ttl_seconds": 900,
        },
    )
    assert r_req.status_code == 200
    ref = r_req.json()["verification_request"]["request_reference"]

    # Step 2: Citizen approves request
    r_consent = client.post(
        f"/api/v1/public-service/verification/requests/{ref}/consent",
        json={"decision": "GRANTED"},
    )
    assert r_consent.status_code == 200
    assert r_consent.json()["verification_status"] == "VERIFIED"

    # Step 3: Institution retrieves verified boolean assertion
    r_res = client.get(f"/api/v1/public-service/verification/requests/{ref}/result")
    assert r_res.status_code == 200
    res_data = r_res.json()
    assert res_data["verification_status"] == "VERIFIED"
    assert res_data["verification"]["raw_files_transferred_bytes"] == 0
    assert len(res_data["verification"]["assertions"]) == len(scopes)


def test_audit_integrity_trail():
    """Phase 24 & 25: Comprehensive audit trail logs all transactions for citizen transparency."""
    citizen_id = "DI-7K4M-9Q2X-8P6R"
    r_hist = client.get(f"/api/v1/public-service/citizen/{citizen_id}/verification-history")
    assert r_hist.status_code == 200
    hist = r_hist.json()
    assert hist["account_id"] == citizen_id
    assert len(hist["verification_history"]) >= 3
    assert len(hist["audit_trail"]) >= 3
