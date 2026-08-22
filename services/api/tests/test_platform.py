from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_student_vertical_slice_generates_trusted_proof() -> None:
    demo = client.post("/api/v1/platform/demo/student").json()

    assert demo["document"]["status"] == "VERIFIED"
    assert demo["verificationCase"]["status"] == "VERIFIED"
    assert demo["transaction"]["state"] == "COMPLETED"
    assert demo["proofResult"]["status"] == "VERIFIED"
    assert demo["proofResult"]["receipt"]["documentShared"] is False

    check = client.post(
        "/api/v1/verification/introspect",
        json={
            "token": demo["proofResult"]["proof"]["token"],
            "audience": demo["proofResult"]["audience"],
        },
    ).json()

    assert check["status"] == "TRUSTED_PROOF"


def test_proof_token_rejects_wrong_audience() -> None:
    demo = client.post("/api/v1/platform/demo/student").json()

    check = client.post(
        "/api/v1/verification/introspect",
        json={"token": demo["proofResult"]["proof"]["token"], "audience": "WRONG_PORTAL"},
    ).json()

    assert check["status"] == "AUDIENCE_MISMATCH"
