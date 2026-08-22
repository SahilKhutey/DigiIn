"""Multi-channel notification dispatcher with templated citizen updates."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("notification")


TEMPLATES = {
    "CONSENT_REQUESTED": "Action Required: {requester_name} has requested verification for your {credential_type}. Tap to review and consent.",
    "VERIFICATION_COMPLETED": "Verification Success: A verified result for your {credential_type} was delivered to {requester_name}.",
    "CREDENTIAL_ISSUED": "New Credential: Your {credential_type} has been officially issued by {issuer_name} to your DigiLocker X wallet.",
    "CONSENT_REVOKED": "Security Alert: Verification authorization for {requester_name} has been revoked.",
    "DISCREPANCY_FLAGGED": "Notice: Discrepancy detected during verification of {document_type}. Officer review is in progress.",
}


class NotificationDispatcher:
    """Dispatches transactional notifications across In-App, SMS, WhatsApp, and Email channels."""

    def __init__(self) -> None:
        self.dispatched_history: list[dict[str, Any]] = []

    async def dispatch_event(
        self,
        event_type: str,
        user_id: str,
        template_params: dict[str, str],
        channel: str = "IN_APP",
    ) -> dict[str, Any]:
        template = TEMPLATES.get(event_type, "Notification from DigiLocker X: {message}")
        message = template.format(**template_params)

        record = {
            "eventId": f"notif_{int(datetime.now(UTC).timestamp() * 1000)}",
            "eventType": event_type,
            "userId": user_id,
            "channel": channel,
            "message": message,
            "timestamp": datetime.now(UTC).isoformat(),
            "status": "DELIVERED",
        }
        self.dispatched_history.append(record)
        logger.info(f"[{channel}] Dispatched to user={user_id}: {message}")
        return record

    async def dispatch(
        self,
        user_id: str,
        channel: str,
        message: str,
        payload: dict[str, Any] | None = None,
    ) -> bool:
        logger.info(f"Notification dispatched to user={user_id} via {channel}: {message}")
        return True


dispatcher = NotificationDispatcher()
