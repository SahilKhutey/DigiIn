"""Phase 7 — Provider Registry.

Central typed registry that DigiIn core uses to discover and dispatch
to authorized issuer, document, and verification providers.
The registry enforces trust validation before every dispatch.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from app.integrations.contracts import (
    DocumentProvider,
    GovernmentVerificationProvider,
    IssuerProvider,
    ProviderCapability,
    ProviderHealthReport,
    ProviderManifest,
    ProviderStatus,
    ProviderType,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Trust Validator
# ---------------------------------------------------------------------------


class TrustValidator:
    """Validates a provider manifest before dispatch."""

    def validate(self, manifest: ProviderManifest) -> tuple[bool, str]:
        if not manifest.is_valid():
            if manifest.status != ProviderStatus.ACTIVE:
                return False, f"Provider '{manifest.provider_id}' is {manifest.status.value}"
            return False, f"Provider '{manifest.provider_id}' validity period has expired"
        return True, "ok"

    def assert_capability(
        self, manifest: ProviderManifest, capability: ProviderCapability
    ) -> None:
        if not manifest.supports(capability):
            raise PermissionError(
                f"Provider '{manifest.provider_id}' does not support capability '{capability.value}'"
            )


# ---------------------------------------------------------------------------
# Health Monitor
# ---------------------------------------------------------------------------


class ProviderHealthMonitor:
    """Polls registered adapters and maintains last-known health state."""

    def __init__(self) -> None:
        self._cache: dict[str, ProviderHealthReport] = {}

    def check(self, provider_id: str, provider: Any) -> ProviderHealthReport:
        try:
            report: ProviderHealthReport = provider.health_check()
            self._cache[provider_id] = report
            return report
        except Exception as exc:
            report = ProviderHealthReport(
                provider_id=provider_id,
                status="unhealthy",
                latency_ms=None,
                checked_at=datetime.now(UTC),
                details={"error": str(exc)},
            )
            self._cache[provider_id] = report
            logger.warning("Health check failed for provider '%s': %s", provider_id, exc)
            return report

    def last_known(self, provider_id: str) -> ProviderHealthReport | None:
        return self._cache.get(provider_id)

    def all_health(self) -> dict[str, ProviderHealthReport]:
        return dict(self._cache)


# ---------------------------------------------------------------------------
# Provider Registry
# ---------------------------------------------------------------------------


class ProviderRegistry:
    """
    Central registry for all integration providers.

    Providers must be registered at startup.  The registry enforces
    trust validation on every lookup so the core never accidentally
    dispatches to a revoked or expired provider.
    """

    def __init__(self) -> None:
        self._issuers: dict[str, IssuerProvider] = {}
        self._doc_providers: dict[str, DocumentProvider] = {}
        self._verifiers: dict[str, GovernmentVerificationProvider] = {}
        self._trust_validator = TrustValidator()
        self._health_monitor = ProviderHealthMonitor()

    # ---- Registration -------------------------------------------------------

    def register_issuer(self, provider: IssuerProvider) -> None:
        manifest = provider.get_manifest()
        ok, reason = self._trust_validator.validate(manifest)
        if not ok:
            raise ValueError(f"Cannot register issuer provider: {reason}")
        self._issuers[manifest.provider_id] = provider
        logger.info("Registered issuer provider: %s (%s)", manifest.name, manifest.provider_id)

    def register_document_provider(self, provider: DocumentProvider) -> None:
        manifest = provider.get_manifest()
        ok, reason = self._trust_validator.validate(manifest)
        if not ok:
            raise ValueError(f"Cannot register document provider: {reason}")
        self._doc_providers[manifest.provider_id] = provider
        logger.info("Registered document provider: %s (%s)", manifest.name, manifest.provider_id)

    def register_verification_provider(self, provider: GovernmentVerificationProvider) -> None:
        manifest = provider.get_manifest()
        ok, reason = self._trust_validator.validate(manifest)
        if not ok:
            raise ValueError(f"Cannot register verification provider: {reason}")
        self._verifiers[manifest.provider_id] = provider
        logger.info(
            "Registered verification provider: %s (%s)", manifest.name, manifest.provider_id
        )

    # ---- Lookups ------------------------------------------------------------

    def get_issuer(self, provider_id: str) -> IssuerProvider:
        provider = self._issuers.get(provider_id)
        if not provider:
            raise KeyError(f"Issuer provider not found: '{provider_id}'")
        manifest = provider.get_manifest()
        ok, reason = self._trust_validator.validate(manifest)
        if not ok:
            raise PermissionError(reason)
        return provider

    def get_document_provider(self, provider_id: str) -> DocumentProvider:
        provider = self._doc_providers.get(provider_id)
        if not provider:
            raise KeyError(f"Document provider not found: '{provider_id}'")
        manifest = provider.get_manifest()
        ok, reason = self._trust_validator.validate(manifest)
        if not ok:
            raise PermissionError(reason)
        return provider

    def get_verification_provider(self, provider_id: str) -> GovernmentVerificationProvider:
        provider = self._verifiers.get(provider_id)
        if not provider:
            raise KeyError(f"Verification provider not found: '{provider_id}'")
        manifest = provider.get_manifest()
        ok, reason = self._trust_validator.validate(manifest)
        if not ok:
            raise PermissionError(reason)
        return provider

    def get_any(self, provider_id: str) -> Any:
        """Return a provider of any type by ID."""
        return (
            self._issuers.get(provider_id)
            or self._doc_providers.get(provider_id)
            or self._verifiers.get(provider_id)
        )

    # ---- Listing ------------------------------------------------------------

    def list_all_manifests(self) -> list[ProviderManifest]:
        manifests: list[ProviderManifest] = []
        for p in self._issuers.values():
            manifests.append(p.get_manifest())
        for p in self._doc_providers.values():
            manifests.append(p.get_manifest())
        for p in self._verifiers.values():
            manifests.append(p.get_manifest())
        return manifests

    def list_by_type(self, provider_type: ProviderType) -> list[ProviderManifest]:
        return [m for m in self.list_all_manifests() if m.provider_type == provider_type]

    def list_by_capability(self, capability: ProviderCapability) -> list[ProviderManifest]:
        return [m for m in self.list_all_manifests() if m.supports(capability)]

    # ---- Health -------------------------------------------------------------

    def health_all(self) -> dict[str, ProviderHealthReport]:
        reports: dict[str, ProviderHealthReport] = {}
        for pid, p in {**self._issuers, **self._doc_providers, **self._verifiers}.items():
            reports[pid] = self._health_monitor.check(pid, p)
        return reports

    def health_one(self, provider_id: str) -> ProviderHealthReport:
        provider = self.get_any(provider_id)
        if not provider:
            raise KeyError(f"Provider not found: '{provider_id}'")
        return self._health_monitor.check(provider_id, provider)

    # ---- Trust validator (public access for lifecycle) ----------------------

    @property
    def trust_validator(self) -> TrustValidator:
        return self._trust_validator


# ---------------------------------------------------------------------------
# Singleton — populated at startup by mock_providers / production config
# ---------------------------------------------------------------------------

provider_registry = ProviderRegistry()
