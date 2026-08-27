"""
Unit and Integration tests for DigiIn Trusted Digital Verification Layer & Account ID Subsystem.
"""

import time
from uuid import UUID

from fastapi.testclient import TestClient

from app.core.ids import (
    ALPHABET,
    EXCLUDED_CHARS,
    create_dual_identity,
    generate_account_id,
    generate_temporary_verification_code,
    is_valid_account_id,
    verify_temporary_verification_code,
)
from app.core.verification_layer import (
    DepartmentVerificationRequest,
    DigiInVerificationLayer,
)
from app.main import app


def test_account_id_specification_compliance():
    """Validates Character Length (17 total, 12 Base32 characters), Base32 Alphabet (no 0, 1, I, O), and DI- prefix."""
    for _ in range(50):
        acc_id = generate_account_id()
        assert len(acc_id) == 17, f"Account ID must be 17 characters in full format: {acc_id}"
        assert acc_id.startswith("DI-"), f"Account ID must start with DI-: {acc_id}"
        assert is_valid_account_id(acc_id), f"Account ID must pass validation: {acc_id}"

        # Extract 12 random characters (excluding prefix and hyphens)
        raw_chars = acc_id.replace("DI-", "").replace("-", "")
        assert len(raw_chars) == 12

        # Verify excluded characters are NEVER present
        for ch in raw_chars:
            assert ch in ALPHABET
            assert ch not in EXCLUDED_CHARS


def test_account_id_uniqueness_and_collision_retry():
    """Tests collision check and retry logic."""
    seen_ids = set()
    for _ in range(100):
        acc_id = generate_account_id(check_collision_fn=lambda cid: cid in seen_ids)
        assert acc_id not in seen_ids
        seen_ids.add(acc_id)


def test_dual_identity_separation():
    """Validates separation of Citizen Public ID and System Internal UUID."""
    dual = create_dual_identity()
    assert dual.public_account_id.startswith("DI-")
    assert len(dual.public_account_id) == 17

    # Internal ID must be a valid UUID
    uuid_obj = UUID(dual.internal_account_id)
    assert str(uuid_obj) == dual.internal_account_id
    assert dual.public_account_id != dual.internal_account_id



def test_temporary_verification_code_lifecycle():
    """Validates 6-digit code generation, hashing, verification, and TTL expiration."""
    account_id = "DI-7K4M-9Q2X-8P6R"
    temp = generate_temporary_verification_code(account_id, validity_seconds=600)

    assert len(temp.code) == 6
    assert temp.code.isdigit()
    assert temp.ttl_seconds == 600
    assert temp.expires_at_epoch > time.time()

    # Successful verification
    valid, msg = verify_temporary_verification_code(
        account_id=account_id,
        candidate_code=temp.code,
        stored_hash=temp.code_hash,
        expires_at_epoch=temp.expires_at_epoch,
    )
    assert valid is True
    assert "VERIFIED" in msg

    # Invalid code rejection
    invalid_code = "000000" if temp.code != "000000" else "111111"
    valid_bad, msg_bad = verify_temporary_verification_code(
        account_id=account_id,
        candidate_code=invalid_code,
        stored_hash=temp.code_hash,
        expires_at_epoch=temp.expires_at_epoch,
    )
    assert valid_bad is False
    assert "INVALID_CODE" in msg_bad

    # Expired code rejection
    valid_exp, msg_exp = verify_temporary_verification_code(
        account_id=account_id,
        candidate_code=temp.code,
        stored_hash=temp.code_hash,
        expires_at_epoch=time.time() - 10,  # Expired in past
    )
    assert valid_exp is False
    assert "EXPIRED" in msg_exp


def test_verification_layer_orchestration_flow():
    """Tests end-to-end verification request with minimum disclosure assertion output."""
    layer = DigiInVerificationLayer()
    req = DepartmentVerificationRequest(
        request_id="req_test_001",
        department_id="dept_du_scholarship_portal",
        department_name="University of Delhi — Scholarship Board",
        digiin_account_id="DI-7K4M-9Q2X-8P6R",
        purpose="Scholarship Merit Verification 2026",
        requested_attributes=[
            "income_status",
            "domicile_status",
            "caste_status",
            "education_qualification",
        ],
    )

    resp = layer.process_verification_request(req)

    assert resp.digiin_account_id == "DI-7K4M-9Q2X-8P6R"
    assert resp.verification_status == "VERIFIED"
    assert resp.raw_files_transferred_bytes == 0  # Invariant: Zero raw bytes
    assert len(resp.assertions) == 4

    # Check that assertions contain level, issuing authority and doc hash
    assertion_keys = [a["attribute"] for a in resp.assertions]
    assert "income_status" in assertion_keys
    assert "domicile_status" in assertion_keys
    assert "caste_status" in assertion_keys
    assert "education_qualification" in assertion_keys

    for a in resp.assertions:
        assert a["status"] == "VERIFIED"
        assert "Level" in a["verification_level"]
        assert len(a["issuing_authority"]) > 0
        assert a["document_hash"] is not None

    # Check audit log entry was created
    trail = layer.get_audit_trail("DI-7K4M-9Q2X-8P6R")
    assert len(trail) >= 1
    assert trail[-1]["action"] == "VERIFICATION_ASSERTION_DISCLOSED"


def test_verification_layer_api_endpoints():
    """Tests HTTP endpoints for attribute verification, temp codes, and QR tokens."""
    client = TestClient(app)

    # 1. Attribute Verification Gateway
    payload = {
        "department_id": "dept_du_scholarship_portal",
        "department_name": "University of Delhi — Scholarship Board",
        "digiin_account_id": "DI-7K4M-9Q2X-8P6R",
        "purpose": "Merit Scholarship Verification",
        "requested_attributes": [
            "income_status",
            "domicile_status",
            "caste_status",
            "education_qualification",
        ],
    }
    r = client.post("/api/v1/public-service/verify-attributes", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["digiin_account_id"] == "DI-7K4M-9Q2X-8P6R"
    assert data["verification_status"] == "VERIFIED"
    assert data["raw_files_transferred_bytes"] == 0
    assert len(data["assertions"]) == 4

    # 2. Temporary Code Generation
    r_code = client.post("/api/v1/public-service/citizen/DI-7K4M-9Q2X-8P6R/temp-code")
    assert r_code.status_code == 200
    code_data = r_code.json()
    assert code_data["status"] == "success"
    assert len(code_data["code"]) == 6
    assert code_data["ttl_seconds"] == 600

    # 3. QR Token Generation
    r_qr = client.get("/api/v1/public-service/citizen/DI-7K4M-9Q2X-8P6R/qr-token")
    assert r_qr.status_code == 200
    qr_data = r_qr.json()
    assert qr_data["status"] == "success"
    assert "digiin://verify" in qr_data["qr_payload"]
    assert qr_data["contains_raw_documents"] is False


def test_phase1_canonical_validator_rules():
    """Phase 1: Validates canonical format DI-XXXX-XXXX-XXXX, cased normalization, and forbidden chars."""
    # Valid IDs
    assert is_valid_account_id("DI-7K4M-9Q2X-8P6R")
    assert is_valid_account_id("di-7k4m-9q2x-8p6r")  # Normalizes case
    assert is_valid_account_id("DI-ABC2-EFG3-HJK4")

    # Invalid: missing prefix
    assert not is_valid_account_id("7K4M-9Q2X-8P6R", allow_legacy=False)
    # Invalid: wrong length / group structure
    assert not is_valid_account_id("DI-7KM-9Q2X-8P6R", allow_legacy=False)
    assert not is_valid_account_id("DI-7K4M9Q2X8P6R", allow_legacy=False)
    assert not is_valid_account_id("DI-7K4M-9Q2X", allow_legacy=False)
    # Invalid: forbidden ambiguous characters (0, 1, I, O)
    assert not is_valid_account_id("DI-7K4M-9Q2X-8P60", allow_legacy=False)  # contains 0
    assert not is_valid_account_id("DI-7K4M-9Q2X-8P61", allow_legacy=False)  # contains 1
    assert not is_valid_account_id("DI-7K4M-9Q2I-8P6R", allow_legacy=False)  # contains I
    assert not is_valid_account_id("DI-7K4M-9Q2O-8P6R", allow_legacy=False)  # contains O


def test_phase1_user_model_auto_assignment():
    """Phase 1: Verifies new User entity receives a valid, unique digiin_account_id."""
    from app.models.entities import User
    user = User(email="test_citizen_p1@example.com", password_hash="dummy_hash")
    assert user.digiin_account_id is not None
    assert is_valid_account_id(user.digiin_account_id)
    assert user.digiin_account_id.startswith("DI-")


def test_phase1_me_endpoint_returns_account_id():
    """Phase 1: Verifies /me endpoint returns citizen's digiin_account_id."""
    client = TestClient(app)
    r = client.get("/api/v1/me")
    assert r.status_code == 200
    data = r.json()
    assert "digiin_account_id" in data
    assert is_valid_account_id(data["digiin_account_id"])


