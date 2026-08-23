"""
DigiIn Observability Subsystem — Dead-Letter Queue (DLQ) & Job Recovery
Captures background jobs that fail maximum retries, isolates them from production traffic, and allows safe operator replay.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DeadLetterJob:
    id: str
    job_type: str  # "VERIFICATION" | "WEBHOOK" | "NOTIFICATION" | "PROOF_MINTING"
    payload: dict[str, Any]
    error_message: str
    retry_count: int
    idempotency_key: str
    quarantined_at: float = field(default_factory=time.time)
    replayed_at: float | None = None
    status: str = "QUARANTINED"  # "QUARANTINED" | "REPLAYED" | "DISCARDED"

class DeadLetterQueueService:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self._dlq_jobs: dict[str, DeadLetterJob] = {}
        self._idempotency_cache: dict[str, Any] = {}

    def handle_job_failure(
        self,
        job_type: str,
        payload: dict[str, Any],
        error_message: str,
        attempt: int,
        idempotency_key: str | None = None
    ) -> DeadLetterJob | None:
        """If attempt exceeds max_retries, quarantine to Dead Letter Queue."""
        if attempt >= self.max_retries:
            dlq_id = f"dlq_{secrets.token_hex(8)}"
            job = DeadLetterJob(
                id=dlq_id,
                job_type=job_type,
                payload=payload,
                error_message=error_message,
                retry_count=attempt,
                idempotency_key=idempotency_key or f"idem_{secrets.token_hex(8)}"
            )
            self._dlq_jobs[dlq_id] = job
            return job
        return None

    def list_quarantined_jobs(self) -> list[DeadLetterJob]:
        return [j for j in self._dlq_jobs.values() if j.status == "QUARANTINED"]

    def replay_job(self, dlq_id: str) -> tuple[bool, str | None, dict[str, Any] | None]:
        """Operator action: replay quarantined job with idempotency deduplication."""
        job = self._dlq_jobs.get(dlq_id)
        if not job or job.status != "QUARANTINED":
            return False, "JOB_NOT_FOUND_OR_ALREADY_PROCESSED", None

        # Check idempotency
        if job.idempotency_key in self._idempotency_cache:
            job.status = "REPLAYED"
            job.replayed_at = time.time()
            return True, "IDEMPOTENT_CACHE_HIT", self._idempotency_cache[job.idempotency_key]

        # Simulate successful replay
        job.status = "REPLAYED"
        job.replayed_at = time.time()
        result = {"status": "SUCCESSFULLY_REPROCESSED", "jobType": job.job_type, "replayedAt": job.replayed_at}
        self._idempotency_cache[job.idempotency_key] = result
        return True, None, result
