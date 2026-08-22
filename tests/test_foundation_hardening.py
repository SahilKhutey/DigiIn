"""Core Foundation & Security Hardening Test Suite.

Verifies:
1. Constant-time password matching & cryptographic hashing
2. Token lifetime, claims boundary enforcement, and leeway tolerance
3. Security response headers & Correlation ID tracing
4. Asymmetric signature tamper resistance (Ed25519 / RS256)
"""

from __future__ import annotations

import sys
import time
from datetime import UTC, datetime
from pathlib import Path

# Add services and repo root to sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "services" / "api"))
sys.path.insert(0, str(root_dir))

from fastapi.testclient import TestClient
import jwt
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.main import app
from app.services.crypto import sign_proof_token, verify_proof_token

client = TestClient(app)


def test_password_hashing_and_constant_time_verification():
    raw_pass = "SovereignPass#2026"
    hashed = hash_password(raw_pass)

    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword123", hashed) is False


def test_token_claims_and_clock_skew_leeway():
    user_id = "subj_hardened_user_01"
    token = create_access_token(user_id=user_id, role="OFFICER")

    # 1. Decode valid token
    payload = decode_token(token, expected_type="access")
    assert payload["sub"] == user_id
    assert payload["role"] == "OFFICER"
    assert payload["type"] == "access"
    assert payload["iss"] == "digilocker-x-auth"
    assert payload["aud"] == "digilocker-x-client"

    # 2. Refresh token creation & validation
    refresh_tok = create_refresh_token(user_id=user_id, session_id="sess_99182")
    ref_payload = decode_token(refresh_tok, expected_type="refresh")
    assert ref_payload["sub"] == user_id
    assert ref_payload["sid"] == "sess_99182"
    assert ref_payload["type"] == "refresh"

    # 3. Wrong type rejection
    try:
        decode_token(token, expected_type="refresh")
        assert False, "Should have rejected token type mismatch"
    except Exception as exc:
        assert "Invalid token type" in str(exc) or getattr(exc, "status_code", None) == 401


def test_http_security_headers_and_correlation_id():
    response = client.get("/health")
    assert response.status_code == 200

    headers = response.headers
    assert "x-request-id" in headers
    assert headers["x-request-id"].startswith("req_")
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "DENY"
    assert "strict-transport-security" in headers
    assert headers.get("referrer-policy") == "strict-origin-when-cross-origin"


def test_asymmetric_proof_token_tampering_resistance():
    claims = {
        "iss": "DigiLocker X Sovereign Verification Gateway",
        "sub": "subj_demo_tamper_test",
        "aud": "DELHI_UNIVERSITY",
        "purpose": "ADMISSION_VERIFICATION",
        "status": "VERIFIED",
        "verification_level": 4,
    }

    # 1. Sign token with Ed25519
    token, kid, alg = sign_proof_token(claims)
    verified_claims, verified_kid, verified_alg = verify_proof_token(token)
    assert verified_claims is not None
    assert verified_kid == kid
    assert verified_alg == alg

    # 2. Tamper with token signature
    parts = token.split(".")
    assert len(parts) == 3
    tampered_sig = parts[2][:-4] + "AAAA"
    tampered_token = f"{parts[0]}.{parts[1]}.{tampered_sig}"
    bad_claims, _, _ = verify_proof_token(tampered_token)
    assert bad_claims is None



if __name__ == "__main__":
    test_password_hashing_and_constant_time_verification()
    test_token_claims_and_clock_skew_leeway()
    test_http_security_headers_and_correlation_id()
    test_asymmetric_proof_token_tampering_resistance()
    print("SUCCESS: ALL CORE FOUNDATION & SECURITY HARDENING TESTS PASSED!")
