"""Phase 7 — Webhook Gateway.

Handles inbound events from external government systems:

  Government System
         │
         │  credential status changed / revocation / etc.
         ▼
  Webhook Gateway
         │
         ├── 1. Authenticate sender (HMAC-SHA256)
         ├── 2. Validate event schema
         ├── 3. Deduplicate by event_id
         ├── 4. Persist event record (webhook_events table)
         └── 5. Dispatch to appropriate handler asynchronously

This module is the entry point for all inbound provider notifications.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.integrations.contracts import InboundWebhookEvent, WebhookEventType
from app.models.entities import Credential, WebhookEvent

logger = logging.getLogger(__name__)

_MOCK_WEBHOOK_SECRET = b"mock-webhook-hmac-secret-2026"
_ENV = os.environ.get("DIGIIN_ENVIRONMENT", "development")


# ---------------------------------------------------------------------------
# Webhook Authenticator
# ---------------------------------------------------------------------------


class WebhookAuthenticator:
    """Validates HMAC-SHA256 signatures on inbound webhook payloads."""

    def __init__(self) -> None:
        # In production: load per-provider secrets from CredentialManager
        self._secrets: dict[str, bytes] = {}
        if _ENV in ("development", "sandbox"):
            # Register mock secret for all mock providers
            self._secrets["mock-cbse-001"] = _MOCK_WEBHOOK_SECRET
            self._secrets["mock-revenue-001"] = _MOCK_WEBHOOK_SECRET
            self._secrets["mock-transport-001"] = _MOCK_WEBHOOK_SECRET
            self._secrets["mock-webhook-provider"] = _MOCK_WEBHOOK_SECRET

    def register_secret(self, provider_id: str, secret: bytes) -> None:
        self._secrets[provider_id] = secret

    def verify(self, provider_id: str, body: bytes, signature: str) -> bool:
        secret = self._secrets.get(provider_id)
        if secret is None:
            logger.warning("No webhook secret for provider '%s'", provider_id)
            return False
        expected = hmac.new(secret, body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)


# ---------------------------------------------------------------------------
# Credential Status Changed Handler
# ---------------------------------------------------------------------------


class CredentialStatusChangedHandler:
    """
    Handles credential.revoked / credential.updated events.

    On revocation:
      - Mark affected Credential entity as SUSPENDED
      - Future verifications against that credential will fail
    """

    def handle_revocation(
        self, db: Session, event: InboundWebhookEvent
    ) -> dict[str, Any]:
        credential_id = event.payload.get("credential_id")
        subject_id = event.payload.get("subject_id")

        affected: list[str] = []

        if credential_id:
            cred = db.query(Credential).filter(Credential.id == credential_id).first()
            if cred and cred.status != "SUSPENDED":
                cred.status = "SUSPENDED"
                db.flush()
                affected.append(credential_id)
                logger.info(
                    "Credential '%s' suspended via webhook from provider '%s'",
                    credential_id,
                    event.provider_id,
                )

        if subject_id and not credential_id:
            # Revoke all active credentials for subject from this issuer
            credentials = (
                db.query(Credential)
                .filter(
                    Credential.issuer_id == event.provider_id,
                    Credential.status.in_(["VERIFIED", "ACTIVE"]),
                )
                .all()
            )
            for cred in credentials:
                cred.status = "SUSPENDED"
                affected.append(cred.id)
            if affected:
                db.flush()
                logger.info(
                    "Bulk credential suspension: %d credentials suspended for subject '%s'",
                    len(affected),
                    subject_id,
                )

        return {
            "affected_credentials": affected,
            "event_id": event.event_id,
            "action": "CREDENTIAL_SUSPENDED",
        }


# ---------------------------------------------------------------------------
# Webhook Gateway
# ---------------------------------------------------------------------------


class WebhookGateway:
    """
    Central entry point for all inbound provider webhook events.

    Responsibilities:
      1. Authenticate sender
      2. Validate and parse event
      3. Deduplicate (same event_id is a no-op)
      4. Persist to webhook_events table
      5. Dispatch to registered handlers
    """

    def __init__(self) -> None:
        self._authenticator = WebhookAuthenticator()
        self._revocation_handler = CredentialStatusChangedHandler()

    def register_provider_secret(self, provider_id: str, secret: bytes) -> None:
        self._authenticator.register_secret(provider_id, secret)

    def receive(
        self,
        db: Session,
        provider_id: str,
        raw_body: bytes,
        signature: str,
    ) -> dict[str, Any]:
        """
        Process one inbound webhook event.

        Returns a status dict describing the outcome.
        Always returns 200-equivalent to prevent retry storms;
        errors are logged internally.
        """
        # 1. Authenticate
        if not self._authenticator.verify(provider_id, raw_body, signature):
            logger.warning(
                "Webhook signature verification failed for provider '%s'", provider_id
            )
            return {"status": "rejected", "reason": "invalid_signature"}

        # 2. Parse
        try:
            payload: dict[str, Any] = json.loads(raw_body)
        except json.JSONDecodeError:
            return {"status": "rejected", "reason": "invalid_json"}

        event_id = payload.get("event_id", "")
        event_type_raw = payload.get("event_type", "")

        # 3. Deduplicate
        existing = db.query(WebhookEvent).filter(WebhookEvent.event_id == event_id).first()
        if existing:
            logger.info("Duplicate webhook event_id '%s' — skipping", event_id)
            return {"status": "deduplicated", "event_id": event_id}

        # 4. Persist
        record = WebhookEvent(
            event_id=event_id,
            provider_id=provider_id,
            event_type=event_type_raw,
            payload_json=json.dumps(payload),
            received_at=datetime.now(UTC),
            processed=False,
        )
        db.add(record)
        db.flush()

        # 5. Dispatch
        try:
            event_type = WebhookEventType(event_type_raw)
        except ValueError:
            logger.warning("Unknown webhook event_type '%s' from '%s'", event_type_raw, provider_id)
            record.processed = True
            db.flush()
            return {"status": "acknowledged", "event_id": event_id, "action": "unknown_type_ignored"}

        inbound = InboundWebhookEvent(
            event_id=event_id,
            provider_id=provider_id,
            event_type=event_type,
            payload=payload,
            raw_signature=signature,
            received_at=datetime.now(UTC),
        )

        result = self._dispatch(db, inbound)
        record.processed = True
        db.commit()

        return {"status": "processed", "event_id": event_id, **result}

    def _dispatch(self, db: Session, event: InboundWebhookEvent) -> dict[str, Any]:
        match event.event_type:
            case WebhookEventType.CREDENTIAL_REVOKED:
                return self._revocation_handler.handle_revocation(db, event)
            case WebhookEventType.ISSUER_SUSPENDED | WebhookEventType.ISSUER_REVOKED:
                logger.warning(
                    "Issuer status event from '%s': %s", event.provider_id, event.event_type
                )
                return {"action": "ISSUER_STATUS_NOTED"}
            case WebhookEventType.DOCUMENT_FLAGGED:
                logger.warning(
                    "Document flagged by provider '%s': %s", event.provider_id, event.payload
                )
                return {"action": "DOCUMENT_FLAGGED_NOTED"}
            case _:
                return {"action": "ACKNOWLEDGED"}


# ---------------------------------------------------------------------------
# Module singleton
# ---------------------------------------------------------------------------

webhook_gateway = WebhookGateway()
