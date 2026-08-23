"""Phase 7 — Providers & Integrations API.

Exposes:
  GET  /api/v1/providers                          — list all registered providers
  GET  /api/v1/providers/{id}                     — get provider manifest + health
  GET  /api/v1/providers/{id}/health              — live health check

  POST /api/v1/integrations/verification          — trigger authoritative verification
  GET  /api/v1/integrations/verification/{id}     — poll async verification job result

  POST /api/v1/integrations/webhooks/{provider}   — receive inbound provider webhook

  GET  /api/v1/integrations/audit                 — integration audit log (OPERATOR only)

Provider administration is restricted to OPERATOR / ADMIN roles.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_role
from app.db import get_db
from app.integrations.audit_trail import audit_logger
from app.integrations.contracts import (
    ClaimVerificationRequest,
    ProviderCapability,
    ProviderType,
)
from app.integrations.lifecycle import lifecycle
from app.integrations.registry import provider_registry
from app.integrations.retry import content_hash, idempotency_store, make_idempotency_key
from app.integrations.webhook_gateway import webhook_gateway
from app.models.entities import IntegrationEvent

router = APIRouter(tags=["providers & integrations"])


# ---------------------------------------------------------------------------
# Provider discovery routes
# ---------------------------------------------------------------------------


@router.get("/providers")
def list_providers(user=Depends(current_user)) -> list[dict[str, Any]]:
    """List all registered providers with their manifests."""
    manifests = provider_registry.list_all_manifests()
    return [m.to_dict() for m in manifests]


@router.get("/providers/{provider_id}")
def get_provider(provider_id: str, user=Depends(current_user)) -> dict[str, Any]:
    """Return provider manifest and last-known health status."""
    provider = provider_registry.get_any(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_id}' not found")
    manifest = provider.get_manifest()
    health = provider_registry.health_one(provider_id)
    return {
        "manifest": manifest.to_dict(),
        "health": {
            "status": health.status,
            "latency_ms": health.latency_ms,
            "checked_at": health.checked_at.isoformat(),
        },
    }


@router.get("/providers/{provider_id}/health")
def provider_health(provider_id: str, user=Depends(current_user)) -> dict[str, Any]:
    """Live health check for a specific provider."""
    provider = provider_registry.get_any(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_id}' not found")
    report = provider_registry.health_one(provider_id)
    return {
        "provider_id": provider_id,
        "status": report.status,
        "latency_ms": report.latency_ms,
        "checked_at": report.checked_at.isoformat(),
        "details": report.details,
    }


# ---------------------------------------------------------------------------
# Authoritative verification routes
# ---------------------------------------------------------------------------


@router.post("/integrations/verification")
def trigger_verification(
    payload: dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(current_user),
) -> dict[str, Any]:
    """
    Trigger authoritative external verification for a claim.

    Required fields:
      - provider_id: str
      - claim_type: str   (e.g. "education", "domicile")
      - capability: str   (e.g. "education", "domicile")
      - raw_claims: dict  (OCR-extracted or citizen-supplied)
    """
    provider_id = payload.get("provider_id", "")
    claim_type = payload.get("claim_type", "")
    capability_raw = payload.get("capability", "education")
    raw_claims = payload.get("raw_claims", {})
    document_id = payload.get("document_id")

    if not provider_id or not claim_type:
        raise HTTPException(status_code=400, detail="provider_id and claim_type are required")

    try:
        capability = ProviderCapability(capability_raw)
    except ValueError:
        capability = ProviderCapability.EDUCATION

    request_id = f"vreq-{uuid.uuid4().hex[:12]}"
    idem_key = make_idempotency_key(
        provider_id, "verify_claim", user.id, content_hash(raw_claims)
    )

    def _do_verify():
        req = ClaimVerificationRequest(
            request_id=request_id,
            correlation_id=idem_key,
            subject_id=user.id,
            claim_type=claim_type,
            capability=capability,
            raw_claims=raw_claims,
            document_id=document_id,
            idempotency_key=idem_key,
        )

        # Determine provider type and dispatch via lifecycle orchestrator
        provider = provider_registry.get_any(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider '{provider_id}' not found")

        manifest = provider.get_manifest()
        if manifest.provider_type == ProviderType.ISSUER_PROVIDER:
            result = lifecycle.verify_claim_via_issuer(provider_id, req)
        else:
            result = lifecycle.verify_authoritative(provider_id, req)

        return {
            "verification_id": request_id,
            "idempotency_key": idem_key,
            "provider_id": result.provider_id,
            "claim_type": result.claim_type,
            "status": result.status,
            "confidence": result.confidence,
            "evidence_reference": result.evidence_reference,
            "verified_at": result.verified_at.isoformat(),
            "source": result.source,
            "simulated": result.simulated,
        }

    with audit_logger.record(
        db, provider_id=provider_id, operation="verify_claim",
        request_id=request_id, correlation_id=idem_key,
    ):
        result_dict, was_cached = idempotency_store.execute_once(
            idem_key, "verify_claim", provider_id, _do_verify
        )

    result_dict["deduplicated"] = was_cached
    return result_dict


@router.get("/integrations/verification/{verification_id}")
def get_verification_result(
    verification_id: str,
    db: Session = Depends(get_db),
    user=Depends(current_user),
) -> dict[str, Any]:
    """Poll the result of a previous verification request by its ID."""
    event = (
        db.query(IntegrationEvent)
        .filter(IntegrationEvent.request_id == verification_id)
        .order_by(IntegrationEvent.started_at.desc())
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail=f"Verification '{verification_id}' not found")
    return {
        "verification_id": verification_id,
        "provider_id": event.provider_id,
        "operation": event.operation,
        "status": event.status,
        "error_code": event.error_code,
        "started_at": event.started_at.isoformat(),
        "completed_at": event.completed_at.isoformat() if event.completed_at else None,
        "retry_count": event.retry_count,
    }


# ---------------------------------------------------------------------------
# Webhook ingest route
# ---------------------------------------------------------------------------


@router.post("/integrations/webhooks/{provider_id}", status_code=status.HTTP_200_OK)
async def receive_webhook(
    provider_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Inbound webhook endpoint for provider events (e.g. credential.revoked).

    Signature is expected in the X-Webhook-Signature header (HMAC-SHA256).
    """
    raw_body = await request.body()
    signature = request.headers.get("X-Webhook-Signature", "")

    result = webhook_gateway.receive(db, provider_id, raw_body, signature)
    return result


# ---------------------------------------------------------------------------
# Integration audit log — OPERATOR / ADMIN only
# ---------------------------------------------------------------------------


@router.get("/integrations/audit")
def get_audit_log(
    provider_id: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    user=Depends(require_role("ADMIN", "OPERATOR", "OFFICER")),
) -> list[dict[str, Any]]:
    """Return integration audit log entries (no PII, no raw document data)."""
    q = db.query(IntegrationEvent)
    if provider_id:
        q = q.filter(IntegrationEvent.provider_id == provider_id)
    events = q.order_by(IntegrationEvent.started_at.desc()).limit(limit).all()
    return [
        {
            "event_id": e.event_id,
            "provider_id": e.provider_id,
            "operation": e.operation,
            "request_id": e.request_id,
            "correlation_id": e.correlation_id,
            "started_at": e.started_at.isoformat(),
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
            "status": e.status,
            "error_code": e.error_code,
            "retry_count": e.retry_count,
        }
        for e in events
    ]
