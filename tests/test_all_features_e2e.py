"""DigiIn (DigiLocker X) Master End-to-End Verification Suite.
Verifies all features, cryptographic protocols, zero-knowledge proofs, federation, and revocation.
"""

import sys
import os

# Add services/api to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "api")))

from fastapi.testclient import TestClient
import app.main

client = TestClient(app.main.app)

def test_01_health_and_jwks():
    print(">>> 1. Testing /health and RFC 7517 JWKS Discovery...")
    res = client.get("/health")
    assert res.status_code == 200, f"Health failed: {res.text}"
    data = res.json()
    assert data["status"] in ["ok", "healthy"]

    res_jwks = client.get("/.well-known/jwks.json")
    assert res_jwks.status_code == 200, f"JWKS failed: {res_jwks.text}"
    jwks = res_jwks.json()
    assert "keys" in jwks and len(jwks["keys"]) > 0
    assert any(k.get("kty") == "OKP" or k.get("alg") == "EdDSA" for k in jwks["keys"])
    print("    [PASS] Health and JWKS root keys active and verifiable.")

def test_02_deterministic_demo_seed_and_reset():
    print(">>> 2. Testing 1-Click Demo Reset and Deterministic State Fixtures...")
    res = client.post("/api/v1/public-service/demo/reset")
    assert res.status_code == 200, f"Reset failed: {res.text}"
    data = res.json()
    assert data["citizen_account_id"] == "DIN-DEMO-001"
    assert data["credentials_count"] >= 3
    print("    [PASS] 1-Click demo reset confirmed with deterministic fixtures.")

def test_03_flagship_scholarship_zero_file_leakage():
    print(">>> 3. Testing 7-Screen Scholarship Flow with 0 Raw Document Leakage...")
    # Step 1: Start scholarship application
    res_apply = client.post(
        "/api/v1/public-service/scholarship/apply",
        json={"citizen_account_id": "DIN-DEMO-001", "service_id": "srv_scholarship_du"},
    )
    assert res_apply.status_code == 200, f"Apply failed: {res_apply.text}"
    app_data = res_apply.json()
    app_id = app_data["application_id"]

    # Step 2: Citizen review with minimal disclosure
    res_review = client.get(f"/api/v1/public-service/scholarship/{app_id}/sharing-review")
    assert res_review.status_code == 200, f"Review failed: {res_review.text}"
    review_data = res_review.json()
    assert review_data["review"]["raw_files_transferred_bytes"] == 0

    # Step 3: Grant consent & mint purpose-bound presentation proof
    res_consent = client.post(
        f"/api/v1/public-service/scholarship/{app_id}/consent-and-submit",
        json={"citizen_account_id": "DIN-DEMO-001", "consent_granted": True},
    )
    assert res_consent.status_code == 200, f"Consent failed: {res_consent.text}"
    consent_data = res_consent.json()
    assert consent_data["raw_files_transferred"] == "0 Bytes"
    assert "proof_id" in consent_data

    # Step 4: Verifier institution reviews proof without raw files
    res_inst = client.get(f"/api/v1/public-service/institution/applications/{app_id}")
    assert res_inst.status_code == 200, f"Institution view failed: {res_inst.text}"
    inst_data = res_inst.json()
    assert inst_data["cryptographic_evidence"]["raw_files_held"] == "0 Bytes (Zero Storage Liability)"
    print("    [PASS] Zero-file scholarship flow executed with 0 raw bytes transferred.")

def test_04_multi_issuer_federation():
    print(">>> 4. Testing Multi-Issuer Authority Federation & Sovereign Issuance...")
    # Step 1: List accredited authorities
    res_iss = client.get("/api/v1/federation/issuers")
    assert res_iss.status_code == 200
    issuers = res_iss.json()["issuers"]
    assert len(issuers) >= 5
    issuer_ids = [i["issuer_id"] for i in issuers]
    assert "ISS-CBSE-01" in issuer_ids
    assert "ISS-REV-DL-01" in issuer_ids

    # Step 2: Issue new sovereign credential
    issue_payload = {
        "issuer_id": "ISS-CBSE-01",
        "citizen_account_id": "DIN-DEMO-001",
        "credential_type": "CLASS_XII_MARKSHEET",
        "title": "CBSE Senior School Certificate",
        "claims": {
            "student_name": "Rahul Sharma",
            "roll_number": "12678901",
            "percentage": 88.5,
            "passed": True,
            "year": 2024,
        },
    }
    res_issue = client.post("/api/v1/federation/issue-credential", json=issue_payload)
    assert res_issue.status_code == 200
    cred = res_issue.json()["credential"]
    cred_id = cred["credential_id"]
    assert cred["status"] == "ACTIVE"
    assert "digital_signature" in cred
    print(f"    [PASS] Multi-issuer federation verified; minted sovereign credential {cred_id}.")
    return cred_id

def test_05_dynamic_revocation_registry(cred_id: str):
    print(">>> 5. Testing Dynamic Cryptographic Revocation Registry...")
    # Step 1: Revoke credential
    revoke_payload = {
        "credential_id": cred_id,
        "issuer_id": "ISS-CBSE-01",
        "reason": "SUSPECTED_FRAUD",
        "reason_description": "Duplicate certificate anomaly flagged for audit.",
        "operator_id": "OFFICER-TEST-01",
    }
    res_rev = client.post("/api/v1/federation/revoke-credential", json=revoke_payload)
    assert res_rev.status_code == 200
    assert res_rev.json()["revocation_record"]["status"] == "REVOKED"

    # Step 2: Check revocation registry
    res_reg = client.get("/api/v1/federation/revocation-registry")
    assert res_reg.status_code == 200
    reg = res_reg.json()
    assert reg["revoked_count"] >= 1
    rev_cids = [r["credential_id"] for r in reg["revocations"]]
    assert cred_id in rev_cids

    # Step 3: Check credential status endpoint
    res_stat = client.get(f"/api/v1/federation/status/{cred_id}")
    assert res_stat.status_code == 200
    assert res_stat.json()["status"] == "REVOKED"
    assert res_stat.json()["is_valid"] is False
    print("    [PASS] Dynamic cryptographic revocation registry verified.")

def test_06_zero_knowledge_predicate_studio():
    print(">>> 6. Testing Zero-Knowledge Predicate Studio & Offline QR Verification...")
    # Step 1: Get templates
    res_tpl = client.get("/api/v1/zk/templates")
    assert res_tpl.status_code == 200
    tpls = res_tpl.json()["templates"]
    assert len(tpls) >= 3

    # Step 2: Evaluate ZK predicates
    eval_payload = {
        "citizen_account_id": "DIN-DEMO-001",
        "audience": "university_admissions_portal",
        "purpose": "Scholarship Assessment",
        "predicates": [
            {
                "predicate_id": "PRED-AGE",
                "label": "Age >= 18",
                "claim_type": "calculated_age",
                "operator": ">=",
                "threshold_value": 18,
            },
            {
                "predicate_id": "PRED-INC",
                "label": "Income <= 8LPA",
                "claim_type": "annual_income_inr",
                "operator": "<=",
                "threshold_value": 800000,
            },
            {
                "predicate_id": "PRED-SCORE",
                "label": "Score >= 75%",
                "claim_type": "cbse_percentage",
                "operator": ">=",
                "threshold_value": 75.0,
            },
        ],
    }
    res_eval = client.post("/api/v1/zk/evaluate-predicates", json=eval_payload)
    assert res_eval.status_code == 200
    eval_data = res_eval.json()
    assert eval_data["all_satisfied"] is True
    assert eval_data["raw_files_transferred_bytes"] == 0
    assert eval_data["pii_leaked_bytes"] == 0
    token = eval_data["presentation_token"]

    # Step 3: Offline QR Verification
    res_qr = client.post(
        "/api/v1/zk/verify-offline-qr",
        json={"qr_payload": token, "audience": "university_admissions_portal"},
    )
    assert res_qr.status_code == 200
    qr_data = res_qr.json()
    assert qr_data["valid"] is True
    assert qr_data["status"] == "VERIFIED_OFFLINE"
    assert qr_data["offline_validated"] is True
    print("    [PASS] Zero-Knowledge Predicate Studio and Offline QR verifier passed.")

def test_07_negative_security_lab():
    print(">>> 7. Testing Negative Security Lab (Tampered & Expired Interception)...")
    res_lab = client.get("/api/v1/public-service/verification-lab")
    assert res_lab.status_code == 200, f"Lab failed: {res_lab.text}"
    lab_tests = res_lab.json()["tests"]
    assert len(lab_tests) >= 5

    # Check tamper detection
    tampered_test = next((t for t in lab_tests if t["test_id"] == "TC-02"), None)
    assert tampered_test is not None
    assert tampered_test["is_valid"] is False

    # Check untrusted issuer detection
    untrusted_test = next((t for t in lab_tests if t["test_id"] == "TC-03"), None)
    assert untrusted_test is not None
    assert untrusted_test["is_valid"] is False

    # Check revoked detection
    revoked_test = next((t for t in lab_tests if t["test_id"] == "TC-04"), None)
    assert revoked_test is not None
    assert revoked_test["is_valid"] is False

    # Check expired detection
    expired_test = next((t for t in lab_tests if t["test_id"] == "TC-05"), None)
    assert expired_test is not None
    assert expired_test["is_valid"] is False
    print("    [PASS] Negative security lab confirmed: all tampered/expired/revoked/untrusted proofs intercepted.")

def run_master_suite():
    print("\n" + "=" * 80)
    print("DIGIIN MASTER END-TO-END VERIFICATION & AUDIT SUITE")
    print("=" * 80)
    test_01_health_and_jwks()
    test_02_deterministic_demo_seed_and_reset()
    test_03_flagship_scholarship_zero_file_leakage()
    cid = test_04_multi_issuer_federation()
    test_05_dynamic_revocation_registry(cid)
    test_06_zero_knowledge_predicate_studio()
    test_07_negative_security_lab()
    print("\n" + "=" * 80)
    print(">>> ALL 7 MASTER TEST PHASES COMPLETED WITH 100% SUCCESS! <<<")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    run_master_suite()
