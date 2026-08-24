"""Phase 9.1 — Asynchronous Job Worker & Dead-Letter Queue (DLQ) Engine.

Executes asynchronous background workloads (OCR, verification, integrations, notifications)
with state-machine transitions, exponential backoff with jitter, and dead-letter queueing.

Job State Machine:
  QUEUED -> RUNNING -> SUCCEEDED
                     -> FAILED (retries exhausted -> DLQ)
                     -> RETRYING (backoff with jitter)
                     -> CANCELLED
"""

from __future__ import annotations

import random
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class JobState(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    CANCELLED = "CANCELLED"


class JobPriority(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


@dataclass
class JobRecord:
    job_id: str
    job_type: str
    payload: dict[str, Any]
    state: JobState = JobState.QUEUED
    priority: JobPriority = JobPriority.NORMAL
    attempts: int = 0
    max_attempts: int = 3
    base_delay_seconds: float = 0.5
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    last_error: str | None = None
    result: dict[str, Any] | None = None
    idempotency_key: str | None = None

    def calculate_backoff(self) -> float:
        """Calculates exponential backoff with randomized jitter."""
        multiplier = 2 ** (self.attempts - 1)
        base = self.base_delay_seconds * multiplier
        jitter = random.uniform(0, 0.1 * base)
        return base + jitter


@dataclass
class DeadLetterRecord:
    dlq_id: str
    job: JobRecord
    failed_at: datetime
    reason: str
    replayed: bool = False
    replayed_at: datetime | None = None


class JobWorkerEngine:
    """Asynchronous job queue and worker execution coordinator with DLQ support."""

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}
        self._queue: list[JobRecord] = []
        self._jobs: dict[str, JobRecord] = {}
        self._dlq: dict[str, DeadLetterRecord] = {}
        self._execution_history: list[JobRecord] = []

    def register_handler(
        self, job_type: str, handler: Callable[[dict[str, Any]], dict[str, Any]]
    ) -> None:
        """Registers an asynchronous processing handler for a given job type."""
        self._handlers[job_type] = handler

    def enqueue(
        self,
        job_type: str,
        payload: dict[str, Any],
        priority: JobPriority = JobPriority.NORMAL,
        max_attempts: int = 3,
        idempotency_key: str | None = None,
    ) -> JobRecord:
        """Enqueues a new background job."""
        if idempotency_key:
            for existing in self._jobs.values():
                if existing.idempotency_key == idempotency_key:
                    return existing

        job_id = f"job_{uuid.uuid4().hex[:12]}"
        job = JobRecord(
            job_id=job_id,
            job_type=job_type,
            payload=payload,
            priority=priority,
            max_attempts=max_attempts,
            idempotency_key=idempotency_key,
        )
        self._jobs[job_id] = job
        self._queue.append(job)
        return job

    def get_job(self, job_id: str) -> JobRecord | None:
        return self._jobs.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job and job.state in (JobState.QUEUED, JobState.RETRYING):
            job.state = JobState.CANCELLED
            job.completed_at = datetime.now(UTC)
            return True
        return False

    def process_next(self) -> JobRecord | None:
        """Executes the next available job in the queue."""
        if not self._queue:
            return None

        # Sort by priority
        priority_order = {
            JobPriority.CRITICAL: 0,
            JobPriority.HIGH: 1,
            JobPriority.NORMAL: 2,
            JobPriority.LOW: 3,
        }
        self._queue.sort(key=lambda j: priority_order.get(j.priority, 2))
        job = self._queue.pop(0)

        if job.state == JobState.CANCELLED:
            return job

        job.state = JobState.RUNNING
        job.started_at = datetime.now(UTC)
        job.attempts += 1

        handler = self._handlers.get(job.job_type)
        if not handler:
            job.state = JobState.FAILED
            job.last_error = f"No handler registered for job type: {job.job_type}"
            job.completed_at = datetime.now(UTC)
            self._send_to_dlq(job, job.last_error)
            return job

        try:
            result = handler(job.payload)
            job.state = JobState.SUCCEEDED
            job.result = result
            job.completed_at = datetime.now(UTC)
            self._execution_history.append(job)
        except Exception as exc:
            job.last_error = str(exc)
            if job.attempts < job.max_attempts:
                job.state = JobState.RETRYING
                self._queue.append(job)
            else:
                job.state = JobState.FAILED
                job.completed_at = datetime.now(UTC)
                self._send_to_dlq(job, str(exc))

        return job

    def process_all(self, max_cycles: int = 100) -> int:
        """Processes all pending jobs until queue is empty or max_cycles is reached."""
        count = 0
        while self._queue and count < max_cycles:
            self.process_next()
            count += 1
        return count

    def _send_to_dlq(self, job: JobRecord, reason: str) -> DeadLetterRecord:
        dlq_id = f"dlq_{uuid.uuid4().hex[:10]}"
        dlq_record = DeadLetterRecord(
            dlq_id=dlq_id,
            job=job,
            failed_at=datetime.now(UTC),
            reason=reason,
        )
        self._dlq[dlq_id] = dlq_record
        return dlq_record

    def list_dlq(self) -> list[dict[str, Any]]:
        """Lists all dead-letter queue records."""
        return [
            {
                "dlq_id": r.dlq_id,
                "job_id": r.job.job_id,
                "job_type": r.job.job_type,
                "attempts": r.job.attempts,
                "failed_at": r.failed_at.isoformat(),
                "reason": r.reason,
                "replayed": r.replayed,
            }
            for r in self._dlq.values()
        ]

    def retry_dlq_item(self, dlq_id: str) -> JobRecord | None:
        """Re-enqueues a failed job from the Dead Letter Queue."""
        record = self._dlq.get(dlq_id)
        if not record:
            return None

        record.replayed = True
        record.replayed_at = datetime.now(UTC)

        job = record.job
        job.state = JobState.QUEUED
        job.attempts = 0
        job.last_error = None
        self._queue.append(job)
        return job

    def get_stats(self) -> dict[str, Any]:
        """Returns runtime queue statistics."""
        return {
            "queue_depth": len(self._queue),
            "total_jobs": len(self._jobs),
            "successful_jobs": sum(
                1 for j in self._jobs.values() if j.state == JobState.SUCCEEDED
            ),
            "failed_jobs": sum(
                1 for j in self._jobs.values() if j.state == JobState.FAILED
            ),
            "retrying_jobs": sum(
                1 for j in self._jobs.values() if j.state == JobState.RETRYING
            ),
            "dlq_count": len(self._dlq),
        }


# Global singleton instance
job_worker = JobWorkerEngine()
