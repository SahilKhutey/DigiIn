"""
DigiIn Privacy & Data Governance — Automated Retention Engine & Legal Holds
Evaluates record retention policies and enforces legal hold locks to prevent premature destruction of evidence.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field


class RetentionAction:
    DELETE = "DELETE"
    ANONYMIZE = "ANONYMIZE"
    ARCHIVE = "ARCHIVE"

@dataclass
class RetentionPolicy:
    id: str
    name: str
    retention_seconds: int
    action: str = RetentionAction.DELETE

@dataclass
class LegalHold:
    id: str
    resource_type: str
    resource_id: str
    reason: str
    created_by: str
    created_at: float = field(default_factory=time.time)
    released_at: float | None = None
    active: bool = True

class RetentionScheduler:
    def __init__(self):
        self._policies: dict[str, RetentionPolicy] = {}
        self._legal_holds: dict[str, LegalHold] = {}
        self._seed_default_policies()

    def _seed_default_policies(self):
        self._policies["RET_DOC_VERIFICATION_30D"] = RetentionPolicy("RET_DOC_VERIFICATION_30D", "30-Day Document Retention", retention_seconds=86400 * 30)
        self._policies["RET_ACCOUNT_LIFETIME"] = RetentionPolicy("RET_ACCOUNT_LIFETIME", "Account Active Lifetime", retention_seconds=86400 * 365 * 10)

    def place_legal_hold(self, resource_type: str, resource_id: str, reason: str, created_by: str) -> LegalHold:
        hold_id = f"hld_{secrets.token_hex(8)}"
        hold = LegalHold(
            id=hold_id,
            resource_type=resource_type,
            resource_id=resource_id,
            reason=reason,
            created_by=created_by,
            active=True
        )
        self._legal_holds[hold_id] = hold
        return hold

    def release_legal_hold(self, hold_id: str) -> bool:
        hold = self._legal_holds.get(hold_id)
        if not hold or not hold.active:
            return False
        hold.active = False
        hold.released_at = time.time()
        return True

    def has_active_legal_hold(self, resource_type: str, resource_id: str) -> bool:
        return any(
            h.active for h in self._legal_holds.values()
            if h.resource_type == resource_type and h.resource_id == resource_id
        )

    def evaluate_record_for_deletion(
        self,
        resource_type: str,
        resource_id: str,
        created_at: float,
        policy_id: str
    ) -> tuple[bool, str]:
        """Evaluates whether a record should be deleted, checking retention age and legal holds."""
        if self.has_active_legal_hold(resource_type, resource_id):
            return False, "LEGAL_HOLD_ACTIVE: Deletion paused due to active legal hold."

        policy = self._policies.get(policy_id)
        if not policy:
            return False, f"POLICY_NOT_FOUND: Retention policy '{policy_id}' is undefined."

        age_seconds = time.time() - created_at
        if age_seconds >= policy.retention_seconds:
            return True, f"RETENTION_EXPIRED: Record exceeded {policy.retention_seconds}s limit. Action: {policy.action}"

        return False, "RETENTION_ACTIVE: Record has not reached expiration threshold."
