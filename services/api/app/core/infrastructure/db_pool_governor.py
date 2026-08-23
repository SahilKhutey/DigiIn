"""
DigiIn Production Infrastructure — Database Connection Pool Governor & Migration Validator
Enforces connection pool capacity limits and validates Expand/Contract zero-downtime database migrations.
"""

from __future__ import annotations


class DatabasePoolGovernor:
    def __init__(self, max_connections: int = 50, reserved_admin_connections: int = 5):
        self.max_connections = max_connections
        self.reserved_admin = reserved_admin_connections
        self.active_connections = 0

    def acquire_connection(self, is_admin: bool = False) -> bool:
        """Enforces connection pool limit protecting PostgreSQL from connection exhaustion."""
        available_pool = self.max_connections if is_admin else (self.max_connections - self.reserved_admin)
        if self.active_connections >= available_pool:
            return False
        self.active_connections += 1
        return True

    def release_connection(self):
        if self.active_connections > 0:
            self.active_connections -= 1

class MigrationPhase:
    EXPAND = "EXPAND"      # Add new nullable columns or tables
    BACKFILL = "BACKFILL"  # Populate historical data
    CONTRACT = "CONTRACT"  # Drop old obsolete columns

class MigrationPlanValidator:
    @staticmethod
    def validate_migration(phase: str, sql_statement: str) -> tuple[bool, str | None]:
        sql_clean = sql_statement.strip().upper()
        # In EXPAND phase, destructive DROP COLUMN is rejected
        if phase == MigrationPhase.EXPAND:
            if "DROP COLUMN" in sql_clean or "DROP TABLE" in sql_clean:
                return False, "DESTRUCTIVE_MIGRATION_REJECTED: Cannot drop columns during EXPAND phase. Use CONTRACT phase after all application pods update."
            if "NOT NULL" in sql_clean and "DEFAULT" not in sql_clean:
                return False, "LOCKING_MIGRATION_REJECTED: Adding NOT NULL columns without default value locks table during live traffic."
        return True, None
