from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_auth_and_full_verification_flow():
    # 1. Health check
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

    # 2. Register unique user
    import time
    email = f"test_{int(time.time()*1000)}@example.com"
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123"},
    )
    assert reg_res.status_code == 200
    tokens = reg_res.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Get current user profile
    me_res = client.get("/api/v1/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

    # 4. Refresh token
    ref_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert ref_res.status_code == 200
    new_tokens = ref_res.json()
    headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}

    # 5. Add demo government credential
    cred_res = client.post(
        "/api/v1/credentials",
        json={
            "credential_type": "CLASS_XII",
            "issuer_id": "org_cbse_gov_in",
            "holder_name": "Test Citizen",
            "passing_year": 2026,
        },
        headers=headers,
    )
    assert cred_res.status_code == 200
    cred_data = cred_res.json()
    assert cred_data["credential_type"] == "CLASS_XII"

    # 6. List credentials
    creds_list = client.get("/api/v1/credentials", headers=headers)
    assert creds_list.status_code == 200
    assert len(creds_list.json()) >= 1

    # 7. Create verification request
    vr_res = client.post(
        "/api/v1/verification/requests",
        json={
            "requester_name": "National Examination Authority",
            "credential_type": "CLASS_XII",
            "purpose": "Examination application eligibility verification",
        },
        headers=headers,
    )
    assert vr_res.status_code == 200
    vr_data = vr_res.json()
    req_id = vr_data["id"]
    assert vr_data["status"] == "PENDING_CONSENT"

    # 8. Grant consent
    consent_res = client.post(
        f"/api/v1/verification/requests/{req_id}/consent",
        json={"decision": "GRANT"},
        headers=headers,
    )
    assert consent_res.status_code == 200
    assert consent_res.json()["status"] == "CONSENT_GRANTED"

    # 9. Run verification against mock issuer
    run_res = client.post(
        f"/api/v1/verification/requests/{req_id}/run",
        headers=headers,
    )
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert run_data["result"] == "VERIFIED"
    assert run_data["verification_level"] == 4
    proof_id = run_data["proof_id"]
    assert proof_id is not None

    # 10. Verify cryptographic proof
    proof_res = client.get(f"/api/v1/proofs/{proof_id}/verify")
    assert proof_res.status_code == 200
    proof_data = proof_res.json()
    assert proof_data["valid"] is True
    assert proof_data["proof"]["verification"] == "VERIFIED"

    # 11. Notifications
    notif_res = client.get("/api/v1/notifications", headers=headers)
    assert notif_res.status_code == 200
    assert len(notif_res.json()) >= 1

    # 12. Government review queue
    gov_res = client.get("/api/v1/government/review-queue", headers=headers)
    assert gov_res.status_code == 200
