"""
DigiIn Privacy & Data Governance — Privacy Audit Logger
Records immutable privacy events for both ALLOWED and DENIED data operations with zero citizen PII.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field


@dataclass
class PrivacyAuditEvent:
    id: str
    actor_id: str
    actor_type: str  # "CITIZEN" | "REVIEWER" | "API_CLIENT" | "SYSTEM"
    action: str      # "READ" | "CREATE" | "UPDATE" | "EXPORT" | "SHARE" | "VERIFY" | "REVOKE" | "DELETE"
    resource_type: str
    resource_id: str
    purpose_code: str | None
    outcome: str     # "ALLOWED" | "DENIED"
    reason: str | None = None
    timestamp: float = field(default_factory=time.time)

class PrivacyAuditLogger:
    def __init__(self):
        self._events: list[PrivacyAuditEvent] = []

    def log_access(
        self,
        actor_id: str,
        actor_type: str,
        action: str,
        resource_type: str,
        resource_id: str,
        purpose_code: str | None,
        outcome: str,
        reason: str | None = None
    ) -> PrivacyAuditEvent:
        eid = f"pau_{secrets.token_hex(8)}"
        evt = PrivacyAuditEvent(
            id=eid,
            actor_id=actor_id,
            actor_type=actor_type,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            purpose_code=purpose_code,
            outcome=outcome,
            reason=reason
        )
        self._events.append(evt)
        return evt

    def list_events_for_resource(self, resource_id: str) -> list[PrivacyAuditEvent]:
        return [e for e in self._events if e.resource_id == resource_id]

    def list_denied_events(self) -> list[PrivacyAuditEvent]:
        return [e for e in self._events if e.outcome == "DENIED"]
