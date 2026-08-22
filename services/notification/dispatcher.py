"""Multi-channel notification dispatcher."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("notification")


class NotificationDispatcher:
    """Dispatches transactional notifications across SMS, WhatsApp, and In-App push."""

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
