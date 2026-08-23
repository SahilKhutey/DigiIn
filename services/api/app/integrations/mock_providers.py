"""Phase 7 — Mock Providers.

Development-only mock implementations of all three provider types.
Every response includes the 'simulated' flag and the 'environment'
tag so mock adapters can NEVER masquerade as real government authorities.

A production guard enforces that these adapters are never registered
when DIGIIN_ENVIRONMENT != 'development'.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

from app.integrations.contracts import (
    AuthMethod,
    ClaimVerificationRequest,
    ClaimVerificationResult,
    ExternalDocumentRequest,
    ExternalDocumentResult,
    ProviderCapability,
    ProviderEnvironment,
    ProviderHealthReport,
    ProviderManifest,
    ProviderStatus,
    ProviderTrustLevel,
    ProviderType,
    WebhookEventType,
)

_SIMULATED_WATERMARK = {
    "provider": "mock-government",
    "environment": "development",
    "simulated": True,
}

_ENV = os.environ.get("DIGIIN_ENVIRONMENT", "development")


def _assert_dev_only(provider_name: str) -> None:
    if _ENV not in ("development", "sandbox"):
        raise RuntimeError(
            f"[SECURITY] Mock provider '{provider_name}' must NOT be registered "
            f"in environment '{_ENV}'.  Use real adapters in production."
        )


# ---------------------------------------------------------------------------
# Mock CBSE Issuer Provider
# ---------------------------------------------------------------------------


class MockCBSEIssuerProvider:
    """Mock Central Board of Secondary Education — implements IssuerProvider."""

    PROVIDER_ID = "mock-cbse-001"

    def __init__(self) -> None:
        _assert_dev_only(self.PROVIDER_ID)

    def get_manifest(self) -> ProviderManifest:
        return ProviderManifest(
            provider_id=self.PROVIDER_ID,
            provider_type=ProviderType.ISSUER_PROVIDER,
            issuer_id="org_cbse_gov_in",
            name="Central Board of Secondary Education (Mock)",
            version="v1",
            environment=ProviderEnvironment.DEVELOPMENT,
            capabilities=[ProviderCapability.EDUCATION, ProviderCapability.DOCUMENT_FETCH],
            auth_method=AuthMethod.NONE,
            status=ProviderStatus.ACTIVE,
            trust_level=ProviderTrustLevel.TRUSTED,
            metadata={**_SIMULATED_WATERMARK},
        )

    def health_check(self) -> ProviderHealthReport:
        return ProviderHealthReport(
            provider_id=self.PROVIDER_ID,
            status="healthy",
            latency_ms=12,
            checked_at=datetime.now(UTC),
            details={**_SIMULATED_WATERMARK},
        )

    def verify_claim(self, request: ClaimVerificationRequest) -> ClaimVerificationResult:
        raw = {
            "qualification": "Senior School Certificate Examination (Class XII)",
            "board": "Central Board of Secondary Education",
            "passing_year": 2026,
            "result": "PASS",
            "stream": "Science",
            "roll_number": request.raw_claims.get("document_number", "MOCK-ROLL-001"),
        }
        return ClaimVerificationResult(
            request_id=request.request_id,
            provider_id=self.PROVIDER_ID,
            claim_type=request.claim_type,
            status="verified",
            confidence=0.97,
            evidence_reference=f"cbse-ev-{request.request_id[:8]}",
            verified_at=datetime.now(UTC),
            source="mock-cbse-001-simulated",
            normalized_claims={
                "qualification": raw["qualification"],
                "issuer_name": raw["board"],
                "passing_year": raw["passing_year"],
                "result": raw["result"],
                "stream": raw["stream"],
                "document_number": raw["roll_number"],
            },
            simulated=True,
        )


# ---------------------------------------------------------------------------
# Mock Revenue / Domicile Verification Provider
# ---------------------------------------------------------------------------


class MockRevenueVerificationProvider:
    """Mock State Revenue Department — implements GovernmentVerificationProvider."""

    PROVIDER_ID = "mock-revenue-001"

    def __init__(self) -> None:
        _assert_dev_only(self.PROVIDER_ID)

    def get_manifest(self) -> ProviderManifest:
        return ProviderManifest(
            provider_id=self.PROVIDER_ID,
            provider_type=ProviderType.VERIFICATION_PROVIDER,
            issuer_id="state_revenue_dept",
            name="State Revenue Department — Domicile & Income (Mock)",
            version="v1",
            environment=ProviderEnvironment.DEVELOPMENT,
            capabilities=[ProviderCapability.DOMICILE, ProviderCapability.INCOME],
            auth_method=AuthMethod.NONE,
            status=ProviderStatus.ACTIVE,
            trust_level=ProviderTrustLevel.TRUSTED,
            metadata={**_SIMULATED_WATERMARK},
        )

    def health_check(self) -> ProviderHealthReport:
        return ProviderHealthReport(
            provider_id=self.PROVIDER_ID,
            status="healthy",
            latency_ms=28,
            checked_at=datetime.now(UTC),
            details={**_SIMULATED_WATERMARK},
        )

    def verify_authoritative(self, request: ClaimVerificationRequest) -> ClaimVerificationResult:
        # Simulates Department A AND Department B response styles both normalizing to DigiIn shape
        return ClaimVerificationResult(
            request_id=request.request_id,
            provider_id=self.PROVIDER_ID,
            claim_type=request.claim_type,
            status="verified",
            confidence=0.95,
            evidence_reference=f"rev-ev-{request.request_id[:8]}",
            verified_at=datetime.now(UTC),
            source="mock-revenue-001-simulated",
            normalized_claims={
                "is_resident": True,
                "district": "Raipur",
                "district_code": "RPR",
                "domicile_status": "VALID",
            },
            simulated=True,
        )

    def get_claim_status(self, subject_id: str, claim_type: str) -> dict[str, Any]:
        return {
            "subject_id": subject_id,
            "claim_type": claim_type,
            "status": "active",
            **_SIMULATED_WATERMARK,
        }


# ---------------------------------------------------------------------------
# Mock Transport / Driving License Provider
# ---------------------------------------------------------------------------


class MockTransportDocumentProvider:
    """Mock MoRTH Sarathi Parivahan — implements DocumentProvider."""

    PROVIDER_ID = "mock-transport-001"

    def __init__(self) -> None:
        _assert_dev_only(self.PROVIDER_ID)

    def get_manifest(self) -> ProviderManifest:
        return ProviderManifest(
            provider_id=self.PROVIDER_ID,
            provider_type=ProviderType.DOCUMENT_PROVIDER,
            issuer_id="morth_sarathi",
            name="MoRTH Sarathi — Driving License (Mock)",
            version="v1",
            environment=ProviderEnvironment.DEVELOPMENT,
            capabilities=[
                ProviderCapability.DRIVING_LICENSE,
                ProviderCapability.VEHICLE_REGISTRATION,
                ProviderCapability.DOCUMENT_FETCH,
            ],
            auth_method=AuthMethod.NONE,
            status=ProviderStatus.ACTIVE,
            trust_level=ProviderTrustLevel.TRUSTED,
            metadata={**_SIMULATED_WATERMARK},
        )

    def health_check(self) -> ProviderHealthReport:
        return ProviderHealthReport(
            provider_id=self.PROVIDER_ID,
            status="healthy",
            latency_ms=45,
            checked_at=datetime.now(UTC),
            details={**_SIMULATED_WATERMARK},
        )

    def fetch_document(self, request: ExternalDocumentRequest) -> ExternalDocumentResult:
        # Document always enters the Phase 2 evidence pipeline — never bypasses it
        mock_pdf = b"%PDF-1.4 Mock Driving License Document " + request.identifier.encode()
        return ExternalDocumentResult(
            document_type=request.document_type,
            raw_content=mock_pdf,
            content_type="application/pdf",
            source_provider_id=self.PROVIDER_ID,
            fetched_at=datetime.now(UTC),
            simulated=True,
            metadata={
                **_SIMULATED_WATERMARK,
                "license_number": request.identifier,
                "license_status": "ACTIVE",
                "validity": "2031-08-01",
                "class": "LMV",
            },
        )

    def list_supported_types(self) -> list[str]:
        return ["DRIVING_LICENSE", "VEHICLE_REGISTRATION_CERTIFICATE"]


# ---------------------------------------------------------------------------
# Mock Webhook Provider
# ---------------------------------------------------------------------------


class MockWebhookProvider:
    """Emits signed mock webhook events for development testing."""

    PROVIDER_ID = "mock-webhook-provider"

    def __init__(self) -> None:
        _assert_dev_only(self.PROVIDER_ID)
        self._mock_secret = b"mock-webhook-hmac-secret-2026"

    def build_revocation_event(
        self,
        credential_id: str,
        subject_id: str,
        issuer_id: str = "mock-cbse-001",
    ) -> dict[str, Any]:
        import hashlib
        import hmac
        import json
        import uuid

        payload: dict[str, Any] = {
            "event_id": f"evt-{uuid.uuid4().hex[:12]}",
            "event_type": WebhookEventType.CREDENTIAL_REVOKED.value,
            "provider_id": issuer_id,
            "credential_id": credential_id,
            "subject_id": subject_id,
            "reason": "SIMULATED_REVOCATION",
            "occurred_at": datetime.now(UTC).isoformat(),
            **_SIMULATED_WATERMARK,
        }
        body = json.dumps(payload, sort_keys=True).encode()
        signature = hmac.new(self._mock_secret, body, hashlib.sha256).hexdigest()
        return {"payload": payload, "signature": signature}

    def get_mock_secret(self) -> bytes:
        """Expose mock secret for test HMAC verification only."""
        return self._mock_secret


# ---------------------------------------------------------------------------
# Bootstrap — register all mock providers into the registry
# ---------------------------------------------------------------------------


def register_mock_providers() -> None:
    """
    Register all development mock providers into the global provider_registry.
    Called once at startup when DIGIIN_ENVIRONMENT == 'development'.
    """
    if _ENV not in ("development", "sandbox"):
        return  # Production guard — never register mocks in production

    from app.integrations.registry import provider_registry

    provider_registry.register_issuer(MockCBSEIssuerProvider())
    provider_registry.register_verification_provider(MockRevenueVerificationProvider())
    provider_registry.register_document_provider(MockTransportDocumentProvider())
