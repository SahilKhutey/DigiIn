import pytest

from app.integrations.issuer import (
    IssuerRegistry,
    MockCBSEIssuer,
    MockUniversityIssuer,
)


@pytest.mark.asyncio
async def test_cbse_issuer_verify_success():
    issuer = MockCBSEIssuer()
    assert issuer.issuer_id == "org_cbse_gov_in"

    health = issuer.health()
    assert health.status == "healthy"
    assert health.issuerName == "Central Board of Secondary Education"

    result = await issuer.verify("CLASS_XII", {"roll_number": "26182910"})
    assert result.is_verified is True
    assert result.level == 4
    assert result.disclosed_claims is not None
    assert result.disclosed_claims["passing_year"] == 2026


@pytest.mark.asyncio
async def test_university_issuer_verify():
    issuer = MockUniversityIssuer()
    assert issuer.issuer_id == "org_university_in"

    result = await issuer.verify("BTECH_DEGREE", {})
    assert result.is_verified is True
    assert result.level == 4
    assert result.disclosed_claims["cgpa"] == 8.85


def test_issuer_registry():
    registry = IssuerRegistry()
    cbse = registry.get("org_cbse_gov_in")
    assert cbse is not None
    assert cbse.name == "Central Board of Secondary Education"

    adapters = registry.list_all()
    assert len(adapters) >= 3
