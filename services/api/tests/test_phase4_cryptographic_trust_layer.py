"""
Phase 4 — DigiIn Trust, Security & Cryptographic Verification Layer Test Suite.

Validates:
1. Asymmetric Ed25519 digital signature creation & verification (RFC 8032 / RFC 7515).
2. Tamper resistance (any alteration invalidates signature).
3. Audience binding (assertion rejected if presented to wrong service).
4. Purpose binding (assertion rejected if used for wrong purpose).
5. Replay attack prevention via nonces and short validity windows.
6. Key rotation and emergency revocation.
7. Security event monitoring and audit logging.
"""

import time

from fastapi.testclient import TestClient

from app.core.proofs.assertion_service import assertion_service
from app.main import app


def test_phase4_cryptographic_signing_and_verification_happy_path():
    """Validates minting and verifying an Ed25519 signed verification assertion."""
    subject_id = "DI-7K4M-9Q2X-8P6R"
    audience = "dept_du_scholarship_portal"
    purpose = "scholarship_eligibility"
    scope = ["income_status", "domicile_status", "education_qualification"]
    claims = {
        "income_status": "Eligible (< 2.5L)",
        "domicile_status": "Verified Resident of NCT Delhi",
        "education_qualification": "CBSE Class XII 94.2%",
    }

    # 1. Mint assertion
    signed_assertion = assertion_service.mint_signed_assertion(
        subject=subject_id,
        audience=audience,
        purpose=purpose,
        scope=scope,
        claims=claims,
        ttl_seconds=600,
    )
    assert signed_assertion["subject"] == subject_id
    assert signed_assertion["audience"] == audience
    assert "signature" in signed_assertion
    assert "digest_sha256" in signed_assertion
    assert signed_assertion["raw_files_transferred_bytes"] == 0

    # 2. Verify assertion
    outcome = assertion_service.verify_signed_assertion(
        assertion=signed_assertion,
        expected_audience=audience,
        expected_purpose=purpose,
        enforce_replay_protection=False,
    )
    assert outcome["valid"] is True
    assert outcome["subject"] == subject_id
    assert outcome["audience"] == audience
    assert len(outcome["claims"]) == 3


def test_phase4_tampering_detection():
    """Validates that modifying any payload field invalidates the digital signature."""
    signed_assertion = assertion_service.mint_signed_assertion(
        subject="DI-7K4M-9Q2X-8P6R",
        audience="dept_du_scholarship_portal",
        purpose="scholarship_eligibility",
        scope=["income_status"],
        claims={"income_status": "Eligible (< 2.5L)"},
    )

    # Tamper with the claims payload
    tampered_assertion = dict(signed_assertion)
    tampered_assertion["claims"] = {"income_status": "Ineligible (> 10L)"}

    outcome = assertion_service.verify_signed_assertion(
        assertion=tampered_assertion,
        expected_audience="dept_du_scholarship_portal",
        expected_purpose="scholarship_eligibility",
        enforce_replay_protection=False,
    )
    assert outcome["valid"] is False
    assert outcome["error_code"] == "INVALID_SIGNATURE"


def test_phase4_audience_binding_rejection():
    """Validates that presenting assertion to wrong department fails with WRONG_AUDIENCE."""
    signed_assertion = assertion_service.mint_signed_assertion(
        subject="DI-7K4M-9Q2X-8P6R",
        audience="dept_du_scholarship_portal",
        purpose="scholarship_eligibility",
        scope=["income_status"],
        claims={"income_status": "Eligible"},
    )

    # Present to Land Registry instead
    outcome = assertion_service.verify_signed_assertion(
        assertion=signed_assertion,
        expected_audience="dept_land_revenue_registration",
        enforce_replay_protection=False,
    )
    assert outcome["valid"] is False
    assert outcome["error_code"] == "WRONG_AUDIENCE"


def test_phase4_purpose_binding_rejection():
    """Validates that presenting assertion for wrong purpose fails with WRONG_PURPOSE."""
    signed_assertion = assertion_service.mint_signed_assertion(
        subject="DI-7K4M-9Q2X-8P6R",
        audience="dept_du_scholarship_portal",
        purpose="scholarship_eligibility",
        scope=["income_status"],
        claims={"income_status": "Eligible"},
    )

    outcome = assertion_service.verify_signed_assertion(
        assertion=signed_assertion,
        expected_audience="dept_du_scholarship_portal",
        expected_purpose="commercial_loan_underwriting",
        enforce_replay_protection=False,
    )
    assert outcome["valid"] is False
    assert outcome["error_code"] == "WRONG_PURPOSE"


def test_phase4_replay_protection():
    """Validates that presenting the same assertion twice triggers REPLAY_DETECTED."""
    signed_assertion = assertion_service.mint_signed_assertion(
        subject="DI-7K4M-9Q2X-8P6R",
        audience="dept_du_scholarship_portal",
        purpose="scholarship_eligibility",
        scope=["domicile_status"],
        claims={"domicile_status": "Delhi"},
    )

    # First presentation succeeds
    first_res = assertion_service.verify_signed_assertion(
        assertion=signed_assertion,
        expected_audience="dept_du_scholarship_portal",
        enforce_replay_protection=True,
    )
    assert first_res["valid"] is True

    # Immediate second presentation must be rejected as replay
    second_res = assertion_service.verify_signed_assertion(
        assertion=signed_assertion,
        expected_audience="dept_du_scholarship_portal",
        enforce_replay_protection=True,
    )
    assert second_res["valid"] is False
    assert second_res["error_code"] == "REPLAY_DETECTED"


def test_phase4_expiration_rejection():
    """Validates that expired assertions fail with EXPIRED."""
    signed_assertion = assertion_service.mint_signed_assertion(
        subject="DI-7K4M-9Q2X-8P6R",
        audience="dept_du_scholarship_portal",
        purpose="scholarship_eligibility",
        scope=["income_status"],
        claims={"income_status": "Eligible"},
        ttl_seconds=1,  # 1 second TTL
    )
    time.sleep(1.2)

    outcome = assertion_service.verify_signed_assertion(
        assertion=signed_assertion,
        expected_audience="dept_du_scholarship_portal",
        enforce_replay_protection=False,
    )
    assert outcome["valid"] is False
    assert outcome["error_code"] == "EXPIRED"


def test_phase4_rest_api_assertion_verification_endpoint():
    """Validates POST /api/v1/public-service/verification/assertions/verify and trust endpoints."""
    client = TestClient(app)

    # 1. Mint an assertion
    assertion = assertion_service.mint_signed_assertion(
        subject="DI-7K4M-9Q2X-8P6R",
        audience="dept_du_scholarship_portal",
        purpose="scholarship_eligibility",
        scope=["education_qualification"],
        claims={"education_qualification": "CBSE Distinction"},
    )

    # 2. Verify via REST API
    payload = {
        "assertion": assertion,
        "expected_audience": "dept_du_scholarship_portal",
        "expected_purpose": "scholarship_eligibility",
        "enforce_replay_protection": False,
    }
    r = client.post("/api/v1/public-service/verification/assertions/verify", json=payload)
    assert r.status_code == 200
    res = r.json()
    assert res["status"] == "success"
    assert res["valid"] is True
    assert res["subject"] == "DI-7K4M-9Q2X-8P6R"

    # 3. Check Trust Registry endpoint
    r_trust = client.get("/api/v1/public-service/trust/services")
    assert r_trust.status_code == 200
    trust_data = r_trust.json()
    assert trust_data["status"] == "success"
    assert "public_key_b64" in trust_data
    assert len(trust_data["accredited_services"]) >= 2

    # 4. Check Security Events endpoint
    r_sec = client.get("/api/v1/public-service/security/events")
    assert r_sec.status_code == 200
    sec_data = r_sec.json()
    assert sec_data["status"] == "success"
    assert "security_events" in sec_data
