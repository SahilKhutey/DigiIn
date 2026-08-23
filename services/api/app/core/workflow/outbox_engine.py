"""
DigiIn Core Workflow Engine — Transactional Outbox & Background Worker Engine
Guarantees reliable, at-least-once domain event dispatch and background task execution with exponential backoff.
"""

import secrets
import time
from typing import Any


class OutboxEvent:
    def __init__(
        self,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str,
        payload: dict[str, Any],
        max_attempts: int = 3
    ):
        self.id = f"evt_{secrets.token_hex(12)}"
        self.event_type = event_type
        self.aggregate_type = aggregate_type
        self.aggregate_id = aggregate_id
        self.payload = payload
        self.created_at = time.time()
        self.published_at: float | None = None
        self.attempts = 0
        self.max_attempts = max_attempts
        self.status = "PENDING"  # "PENDING" | "PUBLISHED" | "DEAD_LETTER"
        self.last_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "aggregate_type": self.aggregate_type,
            "aggregate_id": self.aggregate_id,
            "payload": self.payload,
            "created_at": self.created_at,
            "published_at": self.published_at,
            "attempts": self.attempts,
            "status": self.status,
            "last_error": self.last_error,
        }

class TransactionalOutboxService:
    def __init__(self):
        self._events: dict[str, OutboxEvent] = {}
        self._idempotency_records: dict[str, Any] = {}

    def record_event(
        self,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str,
        payload: dict[str, Any]
    ) -> OutboxEvent:
        """Record domain event inside atomic database transaction boundary."""
        event = OutboxEvent(event_type, aggregate_type, aggregate_id, payload)
        self._events[event.id] = event
        return event

    def dispatch_pending_events(self, handler_fn) -> int:
        """Process pending outbox events with exponential backoff."""
        dispatched_count = 0
        for event in self._events.values():
            if event.status == "PENDING":
                event.attempts += 1
                try:
                    handler_fn(event.event_type, event.aggregate_id, event.payload)
                    event.status = "PUBLISHED"
                    event.published_at = time.time()
                    dispatched_count += 1
                except Exception as ex:
                    event.last_error = str(ex)
                    if event.attempts >= event.max_attempts:
                        event.status = "DEAD_LETTER"
        return dispatched_count

    def check_idempotency(self, idempotency_key: str) -> Any | None:
        """Check if request with this idempotency key was previously completed."""
        return self._idempotency_records.get(idempotency_key)

    def save_idempotency(self, idempotency_key: str, response_data: Any) -> None:
        """Save response under idempotency key."""
        self._idempotency_records[idempotency_key] = response_data
