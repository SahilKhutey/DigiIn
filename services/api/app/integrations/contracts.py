"""Phase 7 — Provider Contracts.

Core Protocol interfaces, manifest models, and claim domain types
that define the integration layer boundary.  DigiIn's core domain
only ever depends on the types defined here; it never imports from
any concrete adapter or external-API client.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class ProviderType(StrEnum):
    ISSUER_PROVIDER = "issuer_provider"
    DOCUMENT_PROVIDER = "document_provider"
    VERIFICATION_PROVIDER = "verification_provider"
    KEY_PROVIDER = "key_provider"


class ProviderStatus(StrEnum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class ProviderEnvironment(StrEnum):
    PRODUCTION = "production"
    STAGING = "staging"
    SANDBOX = "sandbox"
    DEVELOPMENT = "development"


class ProviderTrustLevel(StrEnum):
    SOVEREIGN = "sovereign"       # Constitutional / statutory authority
    STATUTORY = "statutory"       # Legislatively created body
    ACCREDITED = "accredited"     # Government-accredited private body
    TRUSTED = "trusted"           # DigiIn-vetted partner
    UNVERIFIED = "unverified"     # Pending review (never used in production)


class ProviderCapability(StrEnum):
    # Education
    EDUCATION = "education"
    DEGREE = "degree"
    TRANSCRIPT = "transcript"
    # Identity
    IDENTITY = "identity"
    AADHAAR = "aadhaar"
    PAN = "pan"
    # Residency / Civil
    DOMICILE = "domicile"
    INCOME = "income"
    CASTE = "caste"
    BIRTH = "birth"
    # Employment
    EMPLOYMENT = "employment"
    # Vehicle / Transport
    DRIVING_LICENSE = "driving_license"
    VEHICLE_REGISTRATION = "vehicle_registration"
    # Generic
    DOCUMENT_FETCH = "document_fetch"
    REVOCATION_CHECK = "revocation_check"
    KEY_DISCOVERY = "key_discovery"


class AuthMethod(StrEnum):
    OAUTH2 = "oauth2"
    MTLS = "mtls"
    API_KEY = "api_key"
    SIGNED_REQUEST = "signed_request"
    JWT_CLIENT = "jwt_client"
    GOVERNMENT_SSO = "government_sso"
    NONE = "none"  # Development / mock only


# ---------------------------------------------------------------------------
# Provider Manifest
# ---------------------------------------------------------------------------


@dataclass
class ProviderManifest:
    """Immutable descriptor advertised by every registered provider."""

    provider_id: str
    provider_type: ProviderType
    issuer_id: str
    name: str
    version: str
    environment: ProviderEnvironment
    capabilities: list[ProviderCapability]
    auth_method: AuthMethod
    status: ProviderStatus = ProviderStatus.ACTIVE
    trust_level: ProviderTrustLevel = ProviderTrustLevel.TRUSTED
    valid_until: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        if self.status != ProviderStatus.ACTIVE:
            return False
        if self.valid_until and datetime.now(UTC) > self.valid_until:
            return False
        return True

    def supports(self, capability: ProviderCapability) -> bool:
        return capability in self.capabilities

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "provider_type": self.provider_type.value,
            "issuer_id": self.issuer_id,
            "name": self.name,
            "version": self.version,
            "environment": self.environment.value,
            "capabilities": [c.value for c in self.capabilities],
            "auth_method": self.auth_method.value,
            "status": self.status.value,
            "trust_level": self.trust_level.value,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# Claim domain types
# ---------------------------------------------------------------------------


@dataclass
class ClaimVerificationRequest:
    """Standardized inbound claim verification request from DigiIn core."""

    request_id: str
    correlation_id: str
    subject_id: str                   # DigiIn user / credential holder ID
    claim_type: str                   # e.g. "CLASS_XII", "domicile"
    capability: ProviderCapability
    raw_claims: dict[str, Any]        # OCR-extracted or citizen-supplied claims
    document_id: str | None = None
    idempotency_key: str | None = None
    requested_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ClaimVerificationResult:
    """Normalized DigiIn-domain result — always independent of external API shape."""

    request_id: str
    provider_id: str
    claim_type: str
    status: str                        # "verified" | "rejected" | "pending" | "error"
    confidence: float                  # 0.0 – 1.0
    evidence_reference: str            # Opaque reference, not raw data
    verified_at: datetime
    source: str                        # provider name / environment tag
    normalized_claims: dict[str, Any]  # DigiIn canonical field names only
    error_code: str | None = None
    simulated: bool = False            # True only for mock/dev providers

    def to_evidence_dict(self) -> dict[str, Any]:
        return {
            "claim_type": self.claim_type,
            "status": self.status,
            "source": self.source,
            "verified_at": self.verified_at.isoformat(),
            "evidence_reference": self.evidence_reference,
            "confidence": self.confidence,
            "simulated": self.simulated,
        }


# ---------------------------------------------------------------------------
# Document provider types
# ---------------------------------------------------------------------------


@dataclass
class ExternalDocumentRequest:
    subject_id: str
    document_type: str
    identifier: str                 # Roll number, application number, etc.
    correlation_id: str
    idempotency_key: str | None = None


@dataclass
class ExternalDocumentResult:
    """Raw external document payload — MUST enter the Phase 2 evidence pipeline."""

    document_type: str
    raw_content: bytes
    content_type: str               # "application/pdf" | "image/jpeg" | etc.
    source_provider_id: str
    fetched_at: datetime
    simulated: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Provider health
# ---------------------------------------------------------------------------


@dataclass
class ProviderHealthReport:
    provider_id: str
    status: str                     # "healthy" | "degraded" | "unhealthy"
    latency_ms: int | None
    checked_at: datetime
    details: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Protocol interfaces
# ---------------------------------------------------------------------------


@runtime_checkable
class IssuerProvider(Protocol):
    def get_manifest(self) -> ProviderManifest: ...
    def health_check(self) -> ProviderHealthReport: ...
    def verify_claim(self, request: ClaimVerificationRequest) -> ClaimVerificationResult: ...


@runtime_checkable
class DocumentProvider(Protocol):
    def get_manifest(self) -> ProviderManifest: ...
    def health_check(self) -> ProviderHealthReport: ...
    def fetch_document(self, request: ExternalDocumentRequest) -> ExternalDocumentResult: ...
    def list_supported_types(self) -> list[str]: ...


@runtime_checkable
class GovernmentVerificationProvider(Protocol):
    def get_manifest(self) -> ProviderManifest: ...
    def health_check(self) -> ProviderHealthReport: ...
    def verify_authoritative(self, request: ClaimVerificationRequest) -> ClaimVerificationResult: ...
    def get_claim_status(self, subject_id: str, claim_type: str) -> dict[str, Any]: ...


# ---------------------------------------------------------------------------
# Webhook event types
# ---------------------------------------------------------------------------


class WebhookEventType(StrEnum):
    CREDENTIAL_REVOKED = "credential.revoked"
    CREDENTIAL_UPDATED = "credential.updated"
    ISSUER_SUSPENDED = "issuer.suspended"
    ISSUER_REVOKED = "issuer.revoked"
    VERIFICATION_COMPLETED = "verification.completed"
    DOCUMENT_FLAGGED = "document.flagged"


@dataclass
class InboundWebhookEvent:
    event_id: str
    provider_id: str
    event_type: WebhookEventType
    payload: dict[str, Any]
    raw_signature: str
    received_at: datetime = field(default_factory=lambda: datetime.now(UTC))
