"""Phase 7 — Adapter Lifecycle Orchestrator.

Enforces the mandatory lifecycle for every external provider call:

  DISCOVER → CONFIGURE → AUTHENTICATE → HEALTH CHECK
      → REQUEST → VALIDATE RESPONSE → NORMALIZE → DigiIn Domain

No adapter is called without passing through all lifecycle stages.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from app.integrations.auth_boundary import adapter_authenticator
from app.integrations.contracts import (
    ClaimVerificationRequest,
    ClaimVerificationResult,
    DocumentProvider,
    ExternalDocumentRequest,
    ExternalDocumentResult,
    GovernmentVerificationProvider,
    IssuerProvider,
    ProviderCapability,
)
from app.integrations.registry import provider_registry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifecycle stages (for audit / tracing)
# ---------------------------------------------------------------------------


class LifecycleStage:
    DISCOVER = "DISCOVER"
    CONFIGURE = "CONFIGURE"
    AUTHENTICATE = "AUTHENTICATE"
    HEALTH_CHECK = "HEALTH_CHECK"
    REQUEST = "REQUEST"
    VALIDATE_RESPONSE = "VALIDATE_RESPONSE"
    NORMALIZE = "NORMALIZE"
    DOMAIN = "DOMAIN"


class LifecycleError(RuntimeError):
    def __init__(self, stage: str, provider_id: str, detail: str) -> None:
        super().__init__(f"[{stage}] Provider '{provider_id}': {detail}")
        self.stage = stage
        self.provider_id = provider_id
        self.detail = detail


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


class AdapterLifecycleOrchestrator:
    """
    Wraps every external call through the full lifecycle pipeline.

    Each method returns a ClaimVerificationResult or ExternalDocumentResult
    whose data is guaranteed to have passed:
      - Trust validation
      - Auth acquisition
      - Health check (skip_health=True for performance-critical paths)
      - Post-response validation
      - Normalization
    """

    def __init__(self, skip_health_on_repeat: bool = True) -> None:
        self._health_checked: set[str] = set()
        self._skip_health_on_repeat = skip_health_on_repeat

    # ---- Claim Verification via IssuerProvider ------------------------------

    def verify_claim_via_issuer(
        self, provider_id: str, request: ClaimVerificationRequest
    ) -> ClaimVerificationResult:
        # 1. DISCOVER
        provider: IssuerProvider = self._discover_issuer(provider_id)
        manifest = provider.get_manifest()

        # 2. CONFIGURE — trust + capability check
        self._configure(provider_id, manifest, request.capability)

        # 3. AUTHENTICATE (mock/dev adapters use AuthMethod.NONE → no-op)
        self._authenticate(provider_id, manifest)

        # 4. HEALTH CHECK
        self._health_check(provider_id, provider)

        # 5. REQUEST
        started = time.monotonic()
        try:
            raw_result = provider.verify_claim(request)
        except Exception as exc:
            raise LifecycleError(LifecycleStage.REQUEST, provider_id, str(exc)) from exc
        elapsed_ms = int((time.monotonic() - started) * 1000)
        logger.info("Provider '%s' verify_claim completed in %dms", provider_id, elapsed_ms)

        # 6. VALIDATE RESPONSE
        self._validate_claim_result(provider_id, raw_result)

        # 7. NORMALIZE — already done by the adapter; ensure simulated flag
        # 8. DOMAIN — return to caller
        return raw_result

    # ---- Authoritative Verification via GovernmentVerificationProvider -------

    def verify_authoritative(
        self, provider_id: str, request: ClaimVerificationRequest
    ) -> ClaimVerificationResult:
        provider: GovernmentVerificationProvider = self._discover_verifier(provider_id)
        manifest = provider.get_manifest()
        self._configure(provider_id, manifest, request.capability)
        self._authenticate(provider_id, manifest)
        self._health_check(provider_id, provider)

        started = time.monotonic()
        try:
            result = provider.verify_authoritative(request)
        except Exception as exc:
            raise LifecycleError(LifecycleStage.REQUEST, provider_id, str(exc)) from exc
        elapsed_ms = int((time.monotonic() - started) * 1000)
        logger.info(
            "Provider '%s' verify_authoritative completed in %dms", provider_id, elapsed_ms
        )

        self._validate_claim_result(provider_id, result)
        return result

    # ---- Document Fetch via DocumentProvider --------------------------------

    def fetch_document(
        self, provider_id: str, request: ExternalDocumentRequest
    ) -> ExternalDocumentResult:
        """
        Fetch an external document.
        IMPORTANT: the returned ExternalDocumentResult MUST enter the Phase 2
        evidence pipeline (OCR → Classify → Evidence Graph); the caller is
        responsible for enqueuing that pipeline.
        """
        provider: DocumentProvider = self._discover_doc_provider(provider_id)
        manifest = provider.get_manifest()
        self._configure(provider_id, manifest, ProviderCapability.DOCUMENT_FETCH)
        self._authenticate(provider_id, manifest)
        self._health_check(provider_id, provider)

        started = time.monotonic()
        try:
            result = provider.fetch_document(request)
        except Exception as exc:
            raise LifecycleError(LifecycleStage.REQUEST, provider_id, str(exc)) from exc
        elapsed_ms = int((time.monotonic() - started) * 1000)
        logger.info("Provider '%s' fetch_document completed in %dms", provider_id, elapsed_ms)

        self._validate_doc_result(provider_id, result)
        return result

    # ---- Private lifecycle stages -------------------------------------------

    def _discover_issuer(self, provider_id: str) -> IssuerProvider:
        try:
            return provider_registry.get_issuer(provider_id)
        except KeyError as exc:
            raise LifecycleError(LifecycleStage.DISCOVER, provider_id, str(exc)) from exc

    def _discover_verifier(self, provider_id: str) -> GovernmentVerificationProvider:
        try:
            return provider_registry.get_verification_provider(provider_id)
        except KeyError as exc:
            raise LifecycleError(LifecycleStage.DISCOVER, provider_id, str(exc)) from exc

    def _discover_doc_provider(self, provider_id: str) -> DocumentProvider:
        try:
            return provider_registry.get_document_provider(provider_id)
        except KeyError as exc:
            raise LifecycleError(LifecycleStage.DISCOVER, provider_id, str(exc)) from exc

    def _configure(self, provider_id: str, manifest: Any, capability: ProviderCapability) -> None:
        ok, reason = provider_registry.trust_validator.validate(manifest)
        if not ok:
            raise LifecycleError(LifecycleStage.CONFIGURE, provider_id, reason)
        provider_registry.trust_validator.assert_capability(manifest, capability)

    def _authenticate(self, provider_id: str, manifest: Any) -> None:
        try:
            # Build headers — side-effect validates the credential is available
            adapter_authenticator.build_headers(provider_id, manifest.auth_method)
        except Exception as exc:
            raise LifecycleError(LifecycleStage.AUTHENTICATE, provider_id, str(exc)) from exc

    def _health_check(self, provider_id: str, provider: Any) -> None:
        if self._skip_health_on_repeat and provider_id in self._health_checked:
            return
        report = provider.health_check()
        if report.status == "unhealthy":
            raise LifecycleError(
                LifecycleStage.HEALTH_CHECK,
                provider_id,
                f"Provider is unhealthy: {report.details}",
            )
        self._health_checked.add(provider_id)

    def _validate_claim_result(self, provider_id: str, result: ClaimVerificationResult) -> None:
        if not result.request_id or not result.claim_type:
            raise LifecycleError(
                LifecycleStage.VALIDATE_RESPONSE,
                provider_id,
                "ClaimVerificationResult is missing required fields",
            )
        if result.confidence < 0.0 or result.confidence > 1.0:
            raise LifecycleError(
                LifecycleStage.VALIDATE_RESPONSE,
                provider_id,
                f"Invalid confidence value: {result.confidence}",
            )

    def _validate_doc_result(self, provider_id: str, result: ExternalDocumentResult) -> None:
        if not result.raw_content:
            raise LifecycleError(
                LifecycleStage.VALIDATE_RESPONSE, provider_id, "Document content is empty"
            )
        if not result.content_type:
            raise LifecycleError(
                LifecycleStage.VALIDATE_RESPONSE, provider_id, "Document content_type is missing"
            )


# ---------------------------------------------------------------------------
# Module singleton
# ---------------------------------------------------------------------------

lifecycle = AdapterLifecycleOrchestrator()
