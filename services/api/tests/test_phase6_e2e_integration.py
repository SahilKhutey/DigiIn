from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.ids import generate_account_id
from app.crypto.proofs import Proof, _unb64, verify_proof
from app.main import app

client = TestClient(app)


def test_phase6_full_cryptographic_proof_and_offline_verification_pipeline():
    account_id = generate_account_id()

    # 1. Issue an active sovereign credential
    issue_payload = {
        "case_id": f"case_{uuid4().hex[:8]}",
        "account_id": account_id,
        "credential_type": "education.cbse.class_xii",
        "issuer": "Central Board of Secondary Education",
        "claims": [
            {
                "claim_type": "candidate_name",
                "value": "Vikramaditya Roy",
                "source": "CBSE Official Verification Registry",
                "verification_level": "level_4_authoritative",
            },
            {
                "claim_type": "percentage",
                "value": "98.2",
                "source": "CBSE Official Verification Registry",
                "verification_level": "level_4_authoritative",
            },
            {
                "claim_type": "roll_number",
                "value": "7723910",
                "source": "CBSE Official Verification Registry",
                "verification_level": "level_4_authoritative",
            },
        ],
    }
    client.post("/api/v1/credentials/issue", json=issue_payload)

    # 2. External department submits request with nonce
    verifier_id = "dept_iit_delhi_admission"
    req_payload = {
        "verifier_id": verifier_id,
        "account_id": account_id,
        "purpose": "IIT Admission 2026 Eligibility Verification",
        "requested_claim_types": ["candidate_name", "percentage", "roll_number"],
        "ttl_minutes": 30,
    }
    req_res = client.post("/api/v1/gateway/requests", json=req_payload)
    assert req_res.status_code == 200
    request_id = req_res.json()["request_id"]

    # 3. Citizen approves selective disclosure (withholding roll_number)
    consent_payload = {
        "approved_claim_types": ["candidate_name", "percentage"],
        "ttl_minutes": 60,
    }
    client.post(f"/api/v1/gateway/requests/{request_id}/approve", json=consent_payload)

    # 4. Department evaluates request to receive signed Proof envelope
    eval_res = client.post(f"/api/v1/gateway/requests/{request_id}/evaluate")
    assert eval_res.status_code == 200
    eval_data = eval_res.json()

    assert eval_data["valid"] is True
    assert eval_data["claims"] == {
        "candidate_name": "Vikramaditya Roy",
        "percentage": "98.2",
    }
    assert "proof" in eval_data
    proof_dict = eval_data["proof"]
    assert proof_dict["proof_id"].startswith("PRF-")
    assert proof_dict["issuer"] == "digiin"
    assert proof_dict["audience"] == verifier_id
    assert proof_dict["nonce"] == request_id
    assert proof_dict["claims"] == {
        "candidate_name": "Vikramaditya Roy",
        "percentage": "98.2",
    }
    assert len(proof_dict["signature"]) > 20

    # 5. Verifier fetches issuer public keys for independent offline verification
    keys_res = client.get("/api/v1/issuers/digiin/keys")
    assert keys_res.status_code == 200
    key_info = keys_res.json()["keys"][0]
    assert key_info["kty"] == "OKP"
    assert key_info["alg"] == "EdDSA"
    pub_key_bytes = _unb64(key_info["x"])

    # 6. Local / Offline Cryptographic Verification
    proof_obj = Proof(
        proof_id=proof_dict["proof_id"],
        issuer=proof_dict["issuer"],
        audience=proof_dict["audience"],
        issued_at=proof_dict["issued_at"],
        expires_at=proof_dict["expires_at"],
        nonce=proof_dict["nonce"],
        claims=proof_dict["claims"],
        key_id=proof_dict["key_id"],
        signature=proof_dict["signature"],
    )

    assert verify_proof(
        proof_obj,
        public_key=pub_key_bytes,
        expected_issuer="digiin",
        expected_audience=verifier_id,
        expected_nonce=request_id,
    )

    # 7. Online Verifier Verification API
    verify_api_res = client.post(
        "/api/v1/proofs/verify",
        json={
            "proof": proof_dict,
            "expected_issuer": "digiin",
            "expected_audience": verifier_id,
            "expected_nonce": request_id,
        },
    )
    assert verify_api_res.status_code == 200
    assert verify_api_res.json()["valid"] is True
    assert verify_api_res.json()["status"] == "TRUSTED_PROOF_VERIFIED"

    # 8. Tamper Detection Test (altering percentage from 98.2 to 99.9)
    tampered_proof = dict(proof_dict)
    tampered_proof["claims"] = {"candidate_name": "Vikramaditya Roy", "percentage": "99.9"}

    tampered_api_res = client.post(
        "/api/v1/proofs/verify",
        json={
            "proof": tampered_proof,
            "expected_issuer": "digiin",
            "expected_audience": verifier_id,
            "expected_nonce": request_id,
        },
    )
    assert tampered_api_res.status_code == 200
    assert tampered_api_res.json()["valid"] is False
    assert tampered_api_res.json()["status"] == "INVALID_PROOF"

    # 9. Audience Mismatch Test (replaying proof to another department)
    mismatch_audience_res = client.post(
        "/api/v1/proofs/verify",
        json={
            "proof": proof_dict,
            "expected_issuer": "digiin",
            "expected_audience": "dept_another_organization",
            "expected_nonce": request_id,
        },
    )
    assert mismatch_audience_res.status_code == 200
    assert mismatch_audience_res.json()["valid"] is False
