"""
DigiIn Institutional Scale — Legacy Document Migration Framework
Normalizes legacy document databases and PDF archives into standardized DigiIn verified claims via batch pipelines.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any


class MigrationBatchStatus:
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class MigrationBatch:
    batch_id: str
    organization_id: str
    source_system: str
    target_claim_type: str
    total_records: int
    processed_records: int = 0
    successful_records: int = 0
    failed_records: int = 0
    status: str = MigrationBatchStatus.CREATED
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None

class MigrationFramework:
    def __init__(self):
        self._batches: dict[str, MigrationBatch] = {}

    def create_batch(
        self,
        org_id: str,
        source_system: str,
        target_claim: str,
        total_count: int
    ) -> MigrationBatch:
        bid = f"mig_{secrets.token_hex(8)}"
        batch = MigrationBatch(
            batch_id=bid,
            organization_id=org_id,
            source_system=source_system,
            target_claim_type=target_claim,
            total_records=total_count
        )
        self._batches[bid] = batch
        return batch

    def process_legacy_record(self, batch_id: str, raw_record: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        batch = self._batches.get(batch_id)
        if not batch:
            raise ValueError("BATCH_NOT_FOUND")

        batch.processed_records += 1
        # Validate minimum mapping requirements
        if "student_name" in raw_record and "degree" in raw_record:
            batch.successful_records += 1
            transformed = {
                "degree": raw_record["degree"],
                "institution": raw_record.get("institution", "University of Delhi"),
                "year": raw_record.get("year", 2024),
                "migrationStatus": "VALIDATED_FOR_CLAIM"
            }
            if batch.processed_records == batch.total_records:
                batch.status = MigrationBatchStatus.COMPLETED
                batch.completed_at = time.time()
            return True, transformed
        else:
            batch.failed_records += 1
            if batch.processed_records == batch.total_records:
                batch.status = MigrationBatchStatus.COMPLETED
                batch.completed_at = time.time()
            return False, {"error": "INVALID_LEGACY_SCHEMA"}
