from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.ids import generate_account_id
from app.domain.credential_models import (
    Credential,
    CredentialStatus,
    VerifiedClaim,
)
from app.main import app
from app.services.credential_verifier import CredentialVerifier

client = TestClient(app)


def test_phase4_credential_full_lifecycle_and_api():
    account_id = generate_account_id()
    case_id = f"case_{uuid4().hex[:8]}"

    # 1. Issue Credential via API
    payload = {
        "case_id": case_id,
        "account_id": account_id,
        "credential_type": "education.cbse.class_xii",
        "issuer": "Central Board of Secondary Education",
        "claims": [
            {
                "claim_type": "candidate_name",
                "value": "Rahul Sharma",
                "source": "CBSE Official Verification Registry",
                "verification_level": "level_4_authoritative",
            },
            {
                "claim_type": "percentage",
                "value": "91.4",
                "source": "CBSE Official Verification Registry",
                "verification_level": "level_4_authoritative",
            },
        ],
    }

    issue_res = client.post("/api/v1/credentials/issue", json=payload)
    assert issue_res.status_code == 200
    cred_data = issue_res.json()

    crd_id = cred_data["credential_id"]
    assert crd_id.startswith("CRD-")
    assert cred_data["account_id"] == account_id
    assert cred_data["status"] == "active"
    assert len(cred_data["claims"]) == 2

    # 2. List Credentials for Account
    list_res = client.get(f"/api/v1/credentials?account_id={account_id}")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert any(c["credential_id"] == crd_id for c in list_data)

    # 3. Retrieve Single Credential
    get_res = client.get(f"/api/v1/credentials/{crd_id}")
    assert get_res.status_code == 200
    assert get_res.json()["credential_id"] == crd_id

    # 4. Verify Active Credential
    verify_res = client.post("/api/v1/credentials/verify", json={"credential_id": crd_id})
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert v_data["valid"] is True
    assert v_data["reason"] == "active"
    assert v_data["issuer"] == "Central Board of Secondary Education"

    # 5. Revoke Credential
    revoke_res = client.post(f"/api/v1/credentials/{crd_id}/revoke", json={"reason": "Diploma replaced"})
    assert revoke_res.status_code == 200

    # 6. Verify Revoked Credential Fails Safely
    post_revoke_verify = client.post("/api/v1/credentials/verify", json={"credential_id": crd_id})
    assert post_revoke_verify.status_code == 200
    assert post_revoke_verify.json() == {"valid": False, "reason": "revoked", "credential_id": None, "credential_type": None, "issuer": None, "issued_at": None, "expires_at": None}


def test_phase4_credential_verifier_expiry_and_suspension():
    verifier = CredentialVerifier()
    account_id = generate_account_id()

    # Expired Credential
    expired_cred = Credential(
        credential_id="CRD-expired-sample",
        account_id=account_id,
        credential_type="income_certificate",
        issuer="State Revenue Department",
        claims=(
            VerifiedClaim(
                claim_type="income_band",
                value="EWS_ELIGIBLE",
                source="Revenue Dept",
                verification_level="verified",
                verified_at=datetime.now(UTC),
            ),
        ),
        issued_at=datetime.now(UTC) - timedelta(days=400),
        expires_at=datetime.now(UTC) - timedelta(days=35),
        status=CredentialStatus.ACTIVE,
        verification_case_id="case_old_99",
    )
    exp_res = verifier.verify(expired_cred)
    assert exp_res == {"valid": False, "reason": "expired"}

    # Suspended Credential
    suspended_cred = Credential(
        credential_id="CRD-suspended-sample",
        account_id=account_id,
        credential_type="driving_licence",
        issuer="Regional Transport Authority",
        claims=(
            VerifiedClaim(
                claim_type="dl_number",
                value="DL-04-20220011",
                source="RTO Portal",
                verification_level="verified",
                verified_at=datetime.now(UTC),
            ),
        ),
        issued_at=datetime.now(UTC),
        expires_at=None,
        status=CredentialStatus.SUSPENDED,
        verification_case_id="case_rto_11",
    )
    susp_res = verifier.verify(suspended_cred)
    assert susp_res == {"valid": False, "reason": "suspended"}
