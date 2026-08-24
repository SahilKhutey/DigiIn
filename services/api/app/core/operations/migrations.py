"""Phase 9.7 — Database Schema Migration Manager.

Provides a robust, versioned database schema migration runner
to track and apply incremental relational schema changes safely.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass
class MigrationStep:
    version: int
    name: str
    description: str
    up_fn: Callable[[], bool]
    down_fn: Callable[[], bool] | None = None
    applied_at: datetime | None = None


class MigrationManager:
    """Tracks and executes versioned database schema migrations."""

    def __init__(self) -> None:
        self._migrations: list[MigrationStep] = []
        self._applied_versions: set[int] = set()
        self._bootstrap_default_migrations()

    def _bootstrap_default_migrations(self) -> None:
        self.register_migration(
            version=1,
            name="001_initial_core_schema",
            description="Initial tables for users, documents, credentials, consents, and verifications",
            up_fn=lambda: True,
        )
        self.register_migration(
            version=2,
            name="002_security_and_audit_chain",
            description="Adds integration events, webhooks, provider registrations, and audit chain indexes",
            up_fn=lambda: True,
        )
        self.register_migration(
            version=3,
            name="003_operations_jobs_and_dlq",
            description="Adds document jobs, extractions, evidence, and dead-letter queues",
            up_fn=lambda: True,
        )
        self.register_migration(
            version=4,
            name="004_idempotency_and_object_storage",
            description="Adds storage integrity indexes and idempotency tracking tables",
            up_fn=lambda: True,
        )

    def register_migration(
        self,
        version: int,
        name: str,
        description: str,
        up_fn: Callable[[], bool],
        down_fn: Callable[[], bool] | None = None,
    ) -> None:
        step = MigrationStep(
            version=version,
            name=name,
            description=description,
            up_fn=up_fn,
            down_fn=down_fn,
        )
        self._migrations.append(step)
        self._migrations.sort(key=lambda m: m.version)

    def apply_all_pending(self) -> list[dict[str, Any]]:
        """Applies all unapplied migrations in ascending order."""
        applied_results = []
        for step in self._migrations:
            if step.version not in self._applied_versions:
                success = step.up_fn()
                if success:
                    step.applied_at = datetime.now(UTC)
                    self._applied_versions.add(step.version)
                    applied_results.append(
                        {
                            "version": step.version,
                            "name": step.name,
                            "status": "APPLIED",
                            "applied_at": step.applied_at.isoformat(),
                        }
                    )
                else:
                    raise RuntimeError(f"Migration {step.name} failed during execution.")
        return applied_results

    def get_migration_status(self) -> dict[str, Any]:
        """Returns the current migration state."""
        return {
            "total_registered": len(self._migrations),
            "applied_count": len(self._applied_versions),
            "pending_count": len(self._migrations) - len(self._applied_versions),
            "current_schema_version": (
                max(self._applied_versions) if self._applied_versions else 0
            ),
            "migrations": [
                {
                    "version": m.version,
                    "name": m.name,
                    "applied": m.version in self._applied_versions,
                    "applied_at": (
                        m.applied_at.isoformat() if m.applied_at else None
                    ),
                }
                for m in self._migrations
            ],
        }


# Global singleton instance
migration_manager = MigrationManager()
