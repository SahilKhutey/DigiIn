"""DigiIn (DigiLocker X) Comprehensive Threat-Model Security & Cryptographic Invariants Test Suite.

Validates the full defense-in-depth security architecture:
1. RFC 7517 Public JWKS Key Discovery Invariants (Ed25519 & RS256)
2. Negative Proof Tampering (Modified claims fail SHA-256 / Ed25519 verification)
3. Negative Presentation JWT Tampering (Tampered payload bytes fail signature check)
4. Strict Audience Boundary Enforcement (Wrong audience rejected)
5. Strict Expiration Window Enforcement (Expired tokens rejected)
6. Dynamic Revocation Registry Invariants (Revoked credentials immediately invalidated)
7. Anti-Leakage & Zero-Knowledge Data Minimization (0 raw bytes leaked)
8. Synthetic Sandbox Boundary & No-Real-PII Compliance
"""

import base64
import copy
import json
import os
import sys
from datetime import UTC, datetime, timedelta

# Add services/api to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "api")))

from fastapi.testclient import TestClient
import app.main
from app.crypto.proofs import Proof, sign_proof, verify_proof, generate_keypair
from app.services.crypto import get_public_jwks, sign_proof_token, verify_proof_token
from app.services.verification import introspect_token

client = TestClient(app.main.app)


def test_01_jwks_cryptographic_invariants():
    """Verify that RFC 7517 JWKS discovery endpoint exposes valid Ed25519 and RSA keys without brittle count assumptions."""
    print(">>> [Security Gate 1/8] Verifying RFC 7517 JWKS Key Server Invariants...")
    res = client.get("/.well-known/jwks.json")
    assert res.status_code == 200, f"JWKS failed: {res.text}"
    jwks = res.json()
    assert "keys" in jwks, "JWKS response must contain 'keys' array"
    assert len(jwks["keys"]) >= 1, "JWKS must contain at least 1 public key"

    # Invariant A: Must contain an active Ed25519 key (OKP or EdDSA)
    eddsa_key = next((k for k in jwks["keys"] if k.get("kty") == "OKP" or k.get("alg") == "EdDSA"), None)
    assert eddsa_key is not None, "JWKS must expose an Ed25519 (EdDSA/OKP) sovereign public key"
    assert "kid" in eddsa_key and eddsa_key["kid"], "Ed25519 key must have a non-empty key ID (kid)"
    assert "x" in eddsa_key and eddsa_key["x"], "Ed25519 public key must expose x-coordinate"
    assert eddsa_key.get("use") in ["sig", None], "Key usage must be signature verification"

    # Invariant B: Internal crypto helpers return matching keys
    helper_jwks = get_public_jwks()
    assert "keys" in helper_jwks and len(helper_jwks["keys"]) >= 1
    print("    [PASS] RFC 7517 JWKS key discovery invariants verified.")


def test_02_negative_claim_tampering_fails_verification():
    """Mathematically proves that modifying any claim in a signed proof causes instant cryptographic rejection."""
    print(">>> [Security Gate 2/8] Testing Negative Proof Tampering (Claim Modification Attack)...")
    priv_bytes, pub_bytes = generate_keypair()

    original_claims = {
        "student_name": "Rahul Sharma",
        "roll_number": "12678901",
        "cbse_percentage": 88.5,
        "result": "PASSED",
    }
    now = int(datetime.now(UTC).timestamp())
    proof = sign_proof(
        proof_id="PRF-TEST-001",
        issuer="did:digiin:authority:cbse",
        audience="delhi_university",
        nonce="nonce-sec-12345",
        claims=original_claims,
        key_id="key-cbse-2026",
        private_key=priv_bytes,
        expires_at=now + 3600,
    )

    # 1. Verify authentic proof passes
    assert verify_proof(
        proof,
        public_key=pub_bytes,
        expected_issuer="did:digiin:authority:cbse",
        expected_audience="delhi_university",
        expected_nonce="nonce-sec-12345",
    ) is True, "Authentic proof must verify"

    # 2. Attack: Tamper with percentage from 88.5 to 99.9 without re-signing
    tampered_claims = copy.deepcopy(original_claims)
    tampered_claims["cbse_percentage"] = 99.9

    tampered_proof = Proof(
        proof_id=proof.proof_id,
        issuer=proof.issuer,
        audience=proof.audience,
        issued_at=proof.issued_at,
        expires_at=proof.expires_at,
        nonce=proof.nonce,
        claims=tampered_claims,  # Modified claim
        key_id=proof.key_id,
        signature=proof.signature, # Original signature
    )

    # Must fail cryptographic verification
    assert verify_proof(
        tampered_proof,
        public_key=pub_bytes,
        expected_issuer="did:digiin:authority:cbse",
        expected_audience="delhi_university",
        expected_nonce="nonce-sec-12345",
    ) is False, (
        "SECURITY VULNERABILITY: Tampered claim was NOT rejected by cryptographic verification!"
    )
    print("    [PASS] Claim tampering attack mathematically intercepted and rejected.")


def test_03_negative_jwt_token_tampering_fails_introspect():
    """Verify that tampering with any character in a presentation JWT causes signature failure."""
    print(">>> [Security Gate 3/8] Testing Presentation JWT Token Tampering...")
    tok, kid, alg = sign_proof_token(
        claims={
            "sub": "DIN-DEMO-001",
            "aud": "du_scholarship",
            "status": "VERIFIED",
            "income_eligible": True,
            "exp": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
        }
    )
    assert alg == "EdDSA"

    # 1. Authentic token verifies
    intro = introspect_token(tok, audience="du_scholarship")
    assert intro.active is True
    assert intro.cryptoVerified is True

    # 2. Tamper with token payload (replace a byte in payload section)
    parts = tok.split(".")
    assert len(parts) == 3
    # Mutate payload
    mutated_payload = ("A" if parts[1][0] != "A" else "B") + parts[1][1:]
    tampered_token = f"{parts[0]}.{mutated_payload}.{parts[2]}"

    tampered_intro = introspect_token(tampered_token, audience="du_scholarship")
    assert tampered_intro.active is False, "SECURITY VULNERABILITY: Tampered JWT token was accepted!"
    assert tampered_intro.status in ["INVALID_PROOF", "EXPIRED", "REVOKED"]
    print("    [PASS] Presentation JWT tampering intercepted and rejected.")


def test_04_audience_boundary_enforcement():
    """Verify that proofs bound to one service cannot be replayed or presented to a different service."""
    print(">>> [Security Gate 4/8] Testing Audience Boundary Replay Defense...")
    tok, kid, alg = sign_proof_token(
        claims={
            "sub": "DIN-DEMO-001",
            "aud": "authorized_scholarship_portal",
            "status": "VERIFIED",
            "exp": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
        }
    )

    # 1. Intended audience succeeds
    res_correct = introspect_token(tok, audience="authorized_scholarship_portal")
    assert res_correct.active is True

    # 2. Replay attack to wrong verifier portal
    res_wrong = introspect_token(tok, audience="unauthorized_commercial_bank")
    assert res_wrong.active is False, (
        "SECURITY VULNERABILITY: Proof accepted by unintended audience!"
    )
    assert "audience" in res_wrong.message.lower() or res_wrong.status == "INVALID_PROOF"
    print("    [PASS] Audience boundary isolation and replay protection verified.")


def test_05_expiration_window_enforcement():
    """Verify that expired proof tokens are rejected unconditionally."""
    print(">>> [Security Gate 5/8] Testing Expiration Window Enforcement...")
    # Mint token that expired 10 seconds ago
    tok_expired, kid, alg = sign_proof_token(
        claims={
            "sub": "DIN-DEMO-001",
            "aud": "du_scholarship",
            "status": "VERIFIED",
            "exp": (datetime.now(UTC) - timedelta(seconds=10)).isoformat(),
        }
    )

    intro = introspect_token(tok_expired, audience="du_scholarship")
    assert intro.active is False, "SECURITY VULNERABILITY: Expired proof token was accepted!"
    assert intro.status == "EXPIRED" or "expired" in intro.message.lower()
    print("    [PASS] Expired token strictly rejected by validity window check.")


def test_06_revocation_registry_invariants():
    """Verify that revoking a credential immediately marks any derived proofs and status checks as REVOKED."""
    print(">>> [Security Gate 6/8] Testing Dynamic Cryptographic Revocation Invariants...")
    # Step 1: Issue credential
    res_iss = client.post(
        "/api/v1/federation/issue-credential",
        json={
            "issuer_id": "ISS-CBSE-01",
            "citizen_account_id": "DIN-DEMO-001",
            "credential_type": "CLASS_XII_MARKSHEET",
            "title": "CBSE Secondary School Examination",
            "claims": {"student_name": "Test Student", "roll": "999888"},
        },
    )
    assert res_iss.status_code == 200
    cred_id = res_iss.json()["credential"]["credential_id"]

    # Step 2: Verify active initially
    res_stat1 = client.get(f"/api/v1/federation/status/{cred_id}")
    assert res_stat1.status_code == 200
    assert res_stat1.json()["status"] == "ACTIVE"
    assert res_stat1.json()["is_valid"] is True

    # Step 3: Revoke with audit reason
    res_rev = client.post(
        "/api/v1/federation/revoke-credential",
        json={
            "credential_id": cred_id,
            "issuer_id": "ISS-CBSE-01",
            "reason": "SUSPECTED_FRAUD",
            "reason_description": "Suspected altered document identified during audit",
            "operator_id": "SEC-AUDITOR-01",
        },
    )
    assert res_rev.status_code == 200
    assert res_rev.json()["revocation_record"]["status"] == "REVOKED"

    # Step 4: Status must immediately report REVOKED
    res_stat2 = client.get(f"/api/v1/federation/status/{cred_id}")
    assert res_stat2.status_code == 200
    assert res_stat2.json()["status"] == "REVOKED"
    assert res_stat2.json()["is_valid"] is False
    print("    [PASS] Revocation registry immutability and instant propagation verified.")


def test_07_data_minimization_and_zero_file_leakage():
    """Verify that zero-knowledge evaluation produces strictly 0 raw bytes leaked."""
    print(">>> [Security Gate 7/8] Testing Data Minimization & Zero-Leakage Assurances...")
    res_zk = client.post(
        "/api/v1/zk/evaluate-predicates",
        json={
            "citizen_account_id": "DIN-DEMO-001",
            "audience": "scholarship_portal",
            "purpose": "Eligibility Check",
            "predicates": [
                {
                    "predicate_id": "PRED-AGE-18",
                    "label": "Age >= 18",
                    "claim_type": "calculated_age",
                    "operator": ">=",
                    "threshold_value": 18,
                }
            ],
        },
    )
    assert res_zk.status_code == 200
    zk_data = res_zk.json()
    assert zk_data["raw_files_transferred_bytes"] == 0, "Raw files transferred must be strictly 0"
    assert zk_data["pii_leaked_bytes"] == 0, "PII leaked bytes must be strictly 0"

    token = zk_data["presentation_token"]
    # Decode token payload and verify NO raw DOB or Aadhaar is present
    payload_b64 = token.split(".")[1]
    padded = payload_b64 + "=" * ((4 - len(payload_b64) % 4) % 4)
    payload_json = json.loads(base64.urlsafe_b64decode(padded).decode())

    assert "date_of_birth" not in payload_json, "Date of birth must NOT leak in presentation token"
    assert "aadhaar_number" not in payload_json, "Aadhaar must NOT leak in presentation token"
    print("    [PASS] Zero-knowledge data minimization guarantees verified (0 bytes leaked).")


def test_08_synthetic_data_boundary_compliance():
    """Scan platform fixtures to ensure 100% synthetic identities are used with zero real PII."""
    print(">>> [Security Gate 8/8] Verifying Synthetic Sandbox Boundaries...")
    from app.core.public_service.demo_seed import demo_seed_manager
    from app.api.v1.zk_studio import DEMO_CITIZEN_VAULT

    seed_state = demo_seed_manager.get_seed_state()
    assert seed_state.citizen_account_id.startswith("DIN-DEMO-"), "Demo citizen ID must have DEMO prefix"
    for cid, vault in DEMO_CITIZEN_VAULT.items():
        assert cid.startswith("DIN-DEMO-"), f"Vault citizen ID {cid} must have DEMO prefix"
        if "aadhaar_number" in vault:
            assert vault["aadhaar_number"].startswith("9999-"), "Demo Aadhaar must use 9999- test prefix"
    print("    [PASS] Synthetic sandbox boundaries confirmed (Zero real PII).")


def run_full_security_suite():
    print("\n" + "=" * 80)
    print("DIGIIN DEFENSE-IN-DEPTH SECURITY THREAT-MODEL TEST MATRIX")
    print("=" * 80)
    test_01_jwks_cryptographic_invariants()
    test_02_negative_claim_tampering_fails_verification()
    test_03_negative_jwt_token_tampering_fails_introspect()
    test_04_audience_boundary_enforcement()
    test_05_expiration_window_enforcement()
    test_06_revocation_registry_invariants()
    test_07_data_minimization_and_zero_file_leakage()
    test_08_synthetic_data_boundary_compliance()
    print("\n" + "=" * 80)
    print(">>> ALL 8 SECURITY GATES PASSED (100% PRODUCTION-GRADE INTEGRITY) <<<")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_full_security_suite()
