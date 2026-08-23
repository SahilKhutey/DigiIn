"""
DigiIn Service Verification — Verification Request Model & Lifecycle
Defines the authoritative 8-stage request lifecycle: CREATED -> DELIVERED -> VIEWED -> APPROVED -> VERIFYING -> COMPLETED (or DENIED / CANCELLED / EXPIRED / FAILED).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


class RequestLifecycleStatus:
    CREATED = "CREATED"
    DELIVERED = "DELIVERED"
    VIEWED = "VIEWED"
    APPROVED = "APPROVED"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    DENIED = "DENIED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"

VALID_LIFECYCLE_TRANSITIONS = {
    RequestLifecycleStatus.CREATED: [RequestLifecycleStatus.DELIVERED, RequestLifecycleStatus.CANCELLED, RequestLifecycleStatus.EXPIRED],
    RequestLifecycleStatus.DELIVERED: [RequestLifecycleStatus.VIEWED, RequestLifecycleStatus.CANCELLED, RequestLifecycleStatus.EXPIRED],
    RequestLifecycleStatus.VIEWED: [RequestLifecycleStatus.APPROVED, RequestLifecycleStatus.DENIED, RequestLifecycleStatus.EXPIRED],
    RequestLifecycleStatus.APPROVED: [RequestLifecycleStatus.VERIFYING, RequestLifecycleStatus.FAILED],
    RequestLifecycleStatus.VERIFYING: [RequestLifecycleStatus.COMPLETED, RequestLifecycleStatus.FAILED],
    RequestLifecycleStatus.COMPLETED: [],
    RequestLifecycleStatus.DENIED: [],
    RequestLifecycleStatus.CANCELLED: [],
    RequestLifecycleStatus.EXPIRED: [],
    RequestLifecycleStatus.FAILED: [RequestLifecycleStatus.VERIFYING],
}

@dataclass
class ServiceVerificationRequest:
    request_id: str
    service_id: str
    service_name: str
    subject_account_id: str  # e.g., "DGI-7K4M-X9P2-9999"
    purpose: str
    requested_claims: list[str]
    status: str = RequestLifecycleStatus.CREATED
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + (7 * 86400))  # 7 days
    completed_at: float | None = None
    verification_outcome: dict[str, Any] | None = None
    history: list[dict[str, Any]] = field(default_factory=list)

    def transition_to(self, new_status: str, actor: str = "SYSTEM", reason: str = "") -> tuple[bool, str]:
        allowed = VALID_LIFECYCLE_TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            return False, f"INVALID_TRANSITION: Cannot move from {self.status} to {new_status}"

        self.status = new_status
        now = time.time()
        self.history.append({"status": new_status, "timestamp": now, "actor": actor, "reason": reason})

        if new_status in (RequestLifecycleStatus.COMPLETED, RequestLifecycleStatus.DENIED, RequestLifecycleStatus.CANCELLED):
            self.completed_at = now

        return True, f"TRANSITIONED_TO_{new_status}"
