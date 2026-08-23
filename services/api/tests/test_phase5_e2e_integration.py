from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.ids import generate_account_id
from app.main import app

client = TestClient(app)


def test_phase5_gateway_full_lifecycle_and_selective_disclosure():
    account_id = generate_account_id()

    # 1. Issue an active verified credential to the account
    issue_payload = {
        "case_id": f"case_{uuid4().hex[:8]}",
        "account_id": account_id,
        "credential_type": "education.cbse.class_xii",
        "issuer": "Central Board of Secondary Education",
        "claims": [
            {
                "claim_type": "candidate_name",
                "value": "Ananya Verma",
                "source": "CBSE Official Verification Registry",
                "verification_level": "level_4_authoritative",
            },
            {
                "claim_type": "percentage",
                "value": "95.6",
                "source": "CBSE Official Verification Registry",
                "verification_level": "level_4_authoritative",
            },
            {
                "claim_type": "roll_number",
                "value": "6612984",
                "source": "CBSE Official Verification Registry",
                "verification_level": "level_4_authoritative",
            },
        ],
    }
    cred_res = client.post("/api/v1/credentials/issue", json=issue_payload)
    assert cred_res.status_code == 200

    # 2. External department submits a purpose-bound request against the DigiIn Account ID
    req_payload = {
        "verifier_id": "dept_higher_education",
        "account_id": account_id,
        "purpose": "Merit Scholarship 2026 Eligibility",
        "requested_claim_types": ["candidate_name", "percentage", "roll_number"],
        "ttl_minutes": 30,
    }
    req_res = client.post("/api/v1/gateway/requests", json=req_payload)
    assert req_res.status_code == 200
    req_data = req_res.json()
    request_id = req_data["request_id"]
    assert request_id.startswith("REQ-")
    assert req_data["status"] == "pending"

    # 3. Citizen reviews the pending request
    get_res = client.get(f"/api/v1/gateway/requests/{request_id}")
    assert get_res.status_code == 200
    assert get_res.json()["purpose"] == "Merit Scholarship 2026 Eligibility"

    # 4. Citizen grants consent with selective disclosure (approves ONLY candidate_name & percentage, withholding roll_number)
    consent_payload = {
        "approved_claim_types": ["candidate_name", "percentage"],
        "ttl_minutes": 60,
    }
    approve_res = client.post(f"/api/v1/gateway/requests/{request_id}/approve", json=consent_payload)
    assert approve_res.status_code == 200
    assert approve_res.json()["decision"] == "approved"

    # 5. Department evaluates request against gateway
    eval_res = client.post(f"/api/v1/gateway/requests/{request_id}/evaluate")
    assert eval_res.status_code == 200
    eval_data = eval_res.json()

    assert eval_data["valid"] is True
    assert eval_data["purpose"] == "Merit Scholarship 2026 Eligibility"
    # Selective disclosure: only approved claims returned
    assert eval_data["claims"] == {
        "candidate_name": "Ananya Verma",
        "percentage": "95.6",
    }
    assert "roll_number" not in eval_data["claims"]

    # 6. Citizen revokes consent
    revoke_res = client.post(f"/api/v1/gateway/requests/{request_id}/revoke")
    assert revoke_res.status_code == 200
    assert revoke_res.json()["status"] == "revoked"

    # 7. Subsequent evaluation by department fails safely
    post_revoke_eval = client.post(f"/api/v1/gateway/requests/{request_id}/evaluate")
    assert post_revoke_eval.status_code == 200
    assert post_revoke_eval.json()["valid"] is False
    assert "revoked" in post_revoke_eval.json()["reason"].lower()
