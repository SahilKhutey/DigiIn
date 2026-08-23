"""Phase 7 — Integration Audit Trail.

Every external provider call writes a structured IntegrationEvent record.
Rules:
  - Sensitive claim values MUST NOT be logged
  - Raw document bytes MUST NOT be logged
  - Only opaque reference IDs, status codes, and metadata are persisted
"""

from __future__ import annotations

import logging
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any, Generator

from sqlalchemy.orm import Session

from app.models.entities import IntegrationEvent

logger = logging.getLogger(__name__)


class IntegrationAuditLogger:
    """
    Writes one IntegrationEvent row per external provider call.

    Usage (as context manager):
        with audit_logger.record(db, provider_id="mock-cbse-001",
                                  operation="verify_claim",
                                  request_id="req-123",
                                  correlation_id="corr-456") as ctx:
            result = provider.verify_claim(...)
            ctx["status"] = "completed"
    """

    @contextmanager
    def record(
        self,
        db: Session,
        provider_id: str,
        operation: str,
        request_id: str,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        import json

        event_id = f"iev-{uuid.uuid4().hex[:12]}"
        started_at = datetime.now(UTC)
        ctx: dict[str, Any] = {
            "status": "pending",
            "error_code": None,
            "retry_count": 0,
        }

        # Write STARTED row
        event = IntegrationEvent(
            event_id=event_id,
            provider_id=provider_id,
            operation=operation,
            request_id=request_id,
            correlation_id=correlation_id or request_id,
            started_at=started_at,
            status="STARTED",
            metadata_json=json.dumps(metadata or {}),
        )
        db.add(event)
        db.flush()

        try:
            yield ctx
            # Update to completed
            event.status = ctx.get("status", "COMPLETED").upper()
            event.completed_at = datetime.now(UTC)
            event.retry_count = ctx.get("retry_count", 0)
            db.flush()

        except Exception as exc:
            event.status = "ERROR"
            event.error_code = type(exc).__name__[:60]
            event.completed_at = datetime.now(UTC)
            event.retry_count = ctx.get("retry_count", 0)
            db.flush()
            logger.error(
                "Integration call failed — provider='%s' op='%s' req='%s': %s",
                provider_id, operation, request_id, exc,
            )
            raise


# ---------------------------------------------------------------------------
# Module singleton
# ---------------------------------------------------------------------------

audit_logger = IntegrationAuditLogger()
