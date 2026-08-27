"""
Phase 6 — DigiIn Hackathon Sandbox Institutions & Mock Service Test Suite.

Validates:
1. Standardized Scope Registry (identity.basic, income.status, etc.).
2. 2-Tier Decoupled Template Architecture (Institution -> Services -> Scopes).
3. Parameterized testing across all 3 sandbox demo institutions.
4. Strict scope accreditation enforcement.
5. End-to-end sandbox verification and 1-click deterministic reset.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_phase6_list_standardized_scopes():
    """Validates retrieval of standardized verification scope definitions."""
    client = TestClient(app)
    r = client.get("/api/v1/public-service/sandbox/scopes")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["total_scopes"] >= 6
    codes = [s["scope_code"] for s in data["scopes"]]
    assert "identity.basic" in codes
    assert "income.status" in codes
    assert "domicile.status" in codes
    assert "education.qualification" in codes


def test_phase6_list_sandbox_institutions():
    """Validates that all sandbox institutions follow the 2-tier template with hosted services."""
    client = TestClient(app)
    r = client.get("/api/v1/public-service/sandbox/institutions")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["environment"] == "SANDBOX"
    assert data["total_institutions"] >= 3

    codes = [inst["institution_code"] for inst in data["institutions"]]
    assert "EDU-DEMO-001" in codes
    assert "REV-DEMO-001" in codes
    assert "CIT-DEMO-001" in codes

    for inst in data["institutions"]:
        assert len(inst["services"]) >= 1
        assert len(inst["allowed_scopes"]) >= 2


@pytest.mark.parametrize(
    "inst_code, service_code, valid_scopes, invalid_scope",
    [
        ("EDU-DEMO-001", "EDU-SCHOLARSHIP-DEMO", ["education.qualification", "income.status", "domicile.status"], "identity.address"),
        ("REV-DEMO-001", "REV-CERTIFICATE-DEMO", ["identity.basic", "identity.address", "domicile.status"], "education.qualification"),
        ("CIT-DEMO-001", "CIT-PORTAL-DEMO", ["identity.basic", "identity.address"], "income.status"),
    ],
)
def test_phase6_parameterized_institution_template_workflows(
    inst_code: str, service_code: str, valid_scopes: list[str], invalid_scope: str
):
    """Parameterized test running identical accreditation and dispatch tests across all institutions."""
    client = TestClient(app)
    citizen_id = "DI-7K4M-9Q2X-8P6R"

    # 1. Valid verification request
    valid_payload = {
        "institution_code": inst_code,
        "account_id": citizen_id,
        "purpose": f"Standard Sandbox Workflow for {service_code}",
        "requested_scopes": valid_scopes,
        "ttl_seconds": 900,
    }
    r_valid = client.post("/api/v1/public-service/sandbox/verification-requests", json=valid_payload)
    assert r_valid.status_code == 200
    res_valid = r_valid.json()
    assert res_valid["status"] == "success"
    assert res_valid["application"]["status"] == "AWAITING_CONSENT"
    assert res_valid["verification_request"]["request_reference"].startswith("VR-")

    # 2. Unauthorized scope rejection
    invalid_payload = {
        "institution_code": inst_code,
        "account_id": citizen_id,
        "purpose": "Probing Unaccredited Information",
        "requested_scopes": valid_scopes + [invalid_scope],
        "ttl_seconds": 900,
    }
    r_invalid = client.post("/api/v1/public-service/sandbox/verification-requests", json=invalid_payload)
    assert r_invalid.status_code == 403
    assert "UNAUTHORIZED_SCOPE" in r_invalid.json()["detail"]


def test_phase6_deterministic_demo_reset():
    """Validates 1-click demo reset endpoint for live jury reviews."""
    client = TestClient(app)
    r = client.post("/api/v1/public-service/sandbox/reset")
    assert r.status_code == 200
    res = r.json()
    assert res["status"] == "success"
    assert res["demo_citizen"]["account_id"] == "DI-7K4M-9Q2X-8P6R"
    assert res["sandbox_institutions_count"] >= 3
    assert res["total_services_count"] >= 3
