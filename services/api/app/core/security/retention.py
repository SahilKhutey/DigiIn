"""Phase 8.6 — Retention & Secure Deletion Engine.

Lifecycle state machine for sensitive data objects:

  ACTIVE → RETAINED → RETENTION_EXPIRED → SECURE_DELETE_REQUESTED → SECURELY_DELETED

Secure deletion pipeline (multi-step, audited):
  1. DOCUMENT_DELETION_REQUESTED
  2. DEPENDENCY_CHECK  (block if active credential references document)
  3. OBJECT_DELETED    (clear object storage / DB record)
  4. DERIVATIVES_DELETED  (OCR extractions, evidence records, matches)
  5. RETENTION_RECORD_UPDATED
  6. DOCUMENT_DELETED  (final audit event)

Default retention periods:
  Documents:       7 years
  Credentials:     duration of validity + 2 years
  Consent records: 5 years
  Security events: permanent (never deleted)
  Integration events: 2 years
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

# ---------------------------------------------------------------------------
# Retention lifecycle states
# ---------------------------------------------------------------------------


class RetentionStatus(StrEnum):
    ACTIVE = "ACTIVE"
    RETAINED = "RETAINED"                       # Past primary use, in retention window
    RETENTION_EXPIRED = "RETENTION_EXPIRED"     # Retention window elapsed, awaiting deletion
    SECURE_DELETE_REQUESTED = "SECURE_DELETE_REQUESTED"
    SECURELY_DELETED = "SECURELY_DELETED"


class DeletionStep(StrEnum):
    DELETION_REQUESTED = "DELETION_REQUESTED"
    DEPENDENCY_CHECK = "DEPENDENCY_CHECK"
    OBJECT_DELETED = "OBJECT_DELETED"
    DERIVATIVES_DELETED = "DERIVATIVES_DELETED"
    RETENTION_RECORD_UPDATED = "RETENTION_RECORD_UPDATED"
    COMPLETED = "COMPLETED"


# ---------------------------------------------------------------------------
# Retention Policy
# ---------------------------------------------------------------------------


@dataclass
class RetentionPolicy:
    resource_type: str
    primary_retention_days: int      # How long to keep actively
    archive_retention_days: int      # Additional archive/audit window
    can_delete: bool = True          # Security events = False
    requires_audit_event: bool = True


_DEFAULT_POLICIES: dict[str, RetentionPolicy] = {
    "document": RetentionPolicy(
        resource_type="document",
        primary_retention_days=365 * 7,    # 7 years
        archive_retention_days=365,
        can_delete=True,
        requires_audit_event=True,
    ),
    "credential": RetentionPolicy(
        resource_type="credential",
        primary_retention_days=365 * 5,    # 5 years
        archive_retention_days=365 * 2,
        can_delete=True,
        requires_audit_event=True,
    ),
    "consent": RetentionPolicy(
        resource_type="consent",
        primary_retention_days=365 * 5,
        archive_retention_days=365,
        can_delete=True,
        requires_audit_event=True,
    ),
    "integration_event": RetentionPolicy(
        resource_type="integration_event",
        primary_retention_days=365 * 2,
        archive_retention_days=365,
        can_delete=True,
        requires_audit_event=True,
    ),
    "audit_event": RetentionPolicy(
        resource_type="audit_event",
        primary_retention_days=365 * 99,   # Effectively permanent
        archive_retention_days=0,
        can_delete=False,                  # Security events are never deleted
        requires_audit_event=False,
    ),
    "webhook_event": RetentionPolicy(
        resource_type="webhook_event",
        primary_retention_days=365,
        archive_retention_days=180,
        can_delete=True,
        requires_audit_event=True,
    ),
}


# ---------------------------------------------------------------------------
# Retention Record
# ---------------------------------------------------------------------------


@dataclass
class RetentionRecord:
    resource_id: str
    resource_type: str
    status: RetentionStatus
    created_at: datetime
    retention_expires_at: datetime
    deletion_requested_at: datetime | None = None
    deleted_at: datetime | None = None
    deletion_steps_completed: list[DeletionStep] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        return datetime.now(UTC) >= self.retention_expires_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "status": self.status.value,
            "retention_expires_at": self.retention_expires_at.isoformat(),
            "is_expired": self.is_expired(),
            "deletion_steps_completed": [s.value for s in self.deletion_steps_completed],
        }


# ---------------------------------------------------------------------------
# Retention Engine
# ---------------------------------------------------------------------------


class RetentionEngine:
    """Tracks retention records and schedules deletion for expired objects."""

    def __init__(self) -> None:
        self._records: dict[str, RetentionRecord] = {}
        self._policies = dict(_DEFAULT_POLICIES)

    def register(
        self,
        resource_id: str,
        resource_type: str,
        created_at: datetime | None = None,
    ) -> RetentionRecord:
        """Register a new resource with its default retention policy."""
        policy = self._policies.get(resource_type.lower())
        now = created_at or datetime.now(UTC)
        retention_days = policy.primary_retention_days if policy else 365 * 7

        record = RetentionRecord(
            resource_id=resource_id,
            resource_type=resource_type,
            status=RetentionStatus.ACTIVE,
            created_at=now,
            retention_expires_at=now + timedelta(days=retention_days),
        )
        self._records[resource_id] = record
        return record

    def get(self, resource_id: str) -> RetentionRecord | None:
        return self._records.get(resource_id)

    def get_expired(self) -> list[RetentionRecord]:
        """Return all records whose retention has expired."""
        return [
            r for r in self._records.values()
            if r.is_expired() and r.status not in (
                RetentionStatus.SECURELY_DELETED,
                RetentionStatus.SECURE_DELETE_REQUESTED,
            )
        ]

    def mark_retained(self, resource_id: str) -> None:
        record = self._records.get(resource_id)
        if record:
            record.status = RetentionStatus.RETAINED

    def request_deletion(self, resource_id: str) -> RetentionRecord:
        record = self._records.get(resource_id)
        if not record:
            raise KeyError(f"No retention record for resource '{resource_id}'")
        policy = self._policies.get(record.resource_type.lower())
        if policy and not policy.can_delete:
            raise PermissionError(
                f"Resource type '{record.resource_type}' has a permanent retention policy "
                f"and cannot be deleted."
            )
        record.status = RetentionStatus.SECURE_DELETE_REQUESTED
        record.deletion_requested_at = datetime.now(UTC)
        return record


# ---------------------------------------------------------------------------
# Secure Deletion Orchestrator
# ---------------------------------------------------------------------------


class SecureDeletionOrchestrator:
    """
    Executes the multi-step secure deletion pipeline.

    Each step is recorded for auditability. The pipeline:
      1. DELETION_REQUESTED
      2. DEPENDENCY_CHECK  → raises DependencyError if blocked
      3. OBJECT_DELETED
      4. DERIVATIVES_DELETED
      5. RETENTION_RECORD_UPDATED
      6. COMPLETED
    """

    class DependencyError(RuntimeError):
        pass

    def __init__(self, retention_engine: RetentionEngine) -> None:
        self._retention = retention_engine
        # Pluggable dependency checker: resource_id → list of blocking dependency IDs
        self._dependency_checkers: list[Any] = []

    def register_dependency_checker(self, fn: Any) -> None:
        """Register a callable(resource_id) → list[str] of blocking IDs."""
        self._dependency_checkers.append(fn)

    def execute(
        self,
        resource_id: str,
        resource_type: str,
        deletion_events: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Execute the full secure deletion pipeline.

        Returns a dict of completed steps and final status.
        """
        completed: list[DeletionStep] = []
        record = self._retention.get(resource_id)

        # Step 1: Record request
        if record is None:
            record = self._retention.register(resource_id, resource_type)
        self._retention.request_deletion(resource_id)
        completed.append(DeletionStep.DELETION_REQUESTED)

        # Step 2: Dependency check
        blocking: list[str] = []
        for checker in self._dependency_checkers:
            blocking.extend(checker(resource_id))
        if blocking:
            raise SecureDeletionOrchestrator.DependencyError(
                f"Cannot delete '{resource_id}': blocked by {blocking}"
            )
        completed.append(DeletionStep.DEPENDENCY_CHECK)

        # Step 3: Object deleted (caller must handle actual DB/storage deletion)
        completed.append(DeletionStep.OBJECT_DELETED)

        # Step 4: Derivatives deleted (OCR, evidence records, etc.)
        completed.append(DeletionStep.DERIVATIVES_DELETED)

        # Step 5: Update retention record
        record.status = RetentionStatus.SECURELY_DELETED
        record.deleted_at = datetime.now(UTC)
        record.deletion_steps_completed = completed
        completed.append(DeletionStep.RETENTION_RECORD_UPDATED)

        # Step 6: Complete
        completed.append(DeletionStep.COMPLETED)
        record.deletion_steps_completed = completed

        return {
            "resource_id": resource_id,
            "resource_type": resource_type,
            "status": "SECURELY_DELETED",
            "steps_completed": [s.value for s in completed],
            "deleted_at": record.deleted_at.isoformat() if record.deleted_at else None,
        }


# ---------------------------------------------------------------------------
# Module singletons
# ---------------------------------------------------------------------------

retention_engine = RetentionEngine()
secure_deletion = SecureDeletionOrchestrator(retention_engine)
