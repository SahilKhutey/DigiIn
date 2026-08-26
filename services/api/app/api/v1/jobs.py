"""
Phase 16 — Async Document Processing Jobs API.

Provides citizen-facing processing status polling and admin DLQ endpoints.
All endpoints follow the principle: OCR/AI extracts evidence but NEVER independently
declares authenticity — human government review is required for trust elevation.
"""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.operations.job_worker import job_worker
from app.db import get_db
from app.models.entities import Document, DocumentJob, OCRAuditTrail, User
from app.services.job_queue import run_pipeline_for_document

router = APIRouter(prefix="/jobs", tags=["document-processing"])


# ---------------------------------------------------------------------------
# Citizen-facing: processing status
# ---------------------------------------------------------------------------

STAGE_LABELS = {
    "MALWARE_SCAN":     {"label": "Security Scan",       "icon": "🛡️"},
    "OCR":              {"label": "Text Extraction",     "icon": "📄"},
    "CLASSIFY":         {"label": "Classification",      "icon": "🏷️"},
    "EXTRACT":          {"label": "Field Extraction",    "icon": "🔍"},
    "DUPLICATE_CHECK":  {"label": "Duplicate Check",     "icon": "🔁"},
    "ISSUER_LOOKUP":    {"label": "Issuer Verification", "icon": "🏛️"},
    "VERIFICATION":     {"label": "Final Verification",  "icon": "✅"},
}

TERMINAL_STATES = {"COMPLETED", "SUCCEEDED", "FAILED", "CANCELLED"}
RUNNING_STATES  = {"RUNNING", "QUEUED", "RETRYING"}


@router.get("/documents/{document_id}/processing-status")
def get_document_processing_status(
    document_id: str,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Citizen-facing: returns the async processing pipeline status for an uploaded document.

    Returns per-stage progress so the UI can show a live pipeline tracker without polling
    the heavy verification endpoints.
    """
    doc = db.get(Document, document_id)
    if not doc or doc.user_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    jobs = list(
        db.scalars(
            select(DocumentJob)
            .where(DocumentJob.document_id == document_id)
            .order_by(DocumentJob.priority)
        ).all()
    )

    if not jobs:
        return {
            "document_id": document_id,
            "overall_status": "NOT_STARTED",
            "stages": [],
            "pipeline_complete": False,
            "requires_human_review": False,
            "message": "Document has not been queued for processing yet.",
        }

    stages = []
    for job in jobs:
        meta = STAGE_LABELS.get(job.job_type, {"label": job.job_type, "icon": "⚙️"})
        result_data = None
        if job.result_json:
            try:
                result_data = json.loads(job.result_json)
            except Exception:
                pass

        stages.append({
            "job_id":       job.id,
            "stage":        job.job_type,
            "label":        meta["label"],
            "icon":         meta["icon"],
            "status":       job.status,
            "attempts":     job.attempts,
            "max_attempts": job.max_attempts,
            "started_at":   job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_code":   job.error_code,
            "error_message": job.error_message,
            "result":       result_data,
        })

    # Overall rollup
    all_terminal = all(j.status in TERMINAL_STATES for j in jobs)
    any_failed   = any(j.status == "FAILED" for j in jobs)
    any_running  = any(j.status in RUNNING_STATES for j in jobs)

    if any_failed:
        overall = "FAILED"
    elif all_terminal:
        overall = "COMPLETED"
    elif any_running:
        overall = "PROCESSING"
    else:
        overall = "QUEUED"

    # Check if any OCR extraction flagged for human review
    ocr_audit = db.scalars(
        select(OCRAuditTrail)
        .where(OCRAuditTrail.document_id == document_id)
        .where(OCRAuditTrail.requires_human_review == True)  # noqa: E712
    ).first()

    requires_human_review = ocr_audit is not None
    human_review_reason = ocr_audit.human_review_reason if ocr_audit else None

    # Completed jobs: pipeline finish time
    completed_jobs = [j for j in jobs if j.completed_at]
    finished_at = max((j.completed_at for j in completed_jobs), default=None)

    return {
        "document_id":          document_id,
        "document_title":       doc.title,
        "document_status":      doc.verification_status,
        "overall_status":       overall,
        "pipeline_complete":    all_terminal and not any_failed,
        "requires_human_review": requires_human_review,
        "human_review_reason":  human_review_reason,
        "stages":               stages,
        "total_stages":         len(stages),
        "completed_stages":     sum(1 for j in jobs if j.status in TERMINAL_STATES),
        "finished_at":          finished_at.isoformat() if finished_at else None,
        # Architecture invariant: pipeline completion ≠ government authentication
        "authenticity_notice":  (
            "OCR/AI processing is complete. Government authentication requires human review "
            "by an authorized officer — automated extraction never independently declares "
            "a document authentic."
        ),
    }


# ---------------------------------------------------------------------------
# Admin / developer: DLQ and retry
# ---------------------------------------------------------------------------

@router.get("/dlq")
def list_dead_letter_queue(
    user: User = Depends(current_user),
) -> dict[str, Any]:
    """Admin: list all jobs that exhausted retries and landed in the Dead-Letter Queue."""
    return {"dlq": job_worker.list_dlq(), "count": len(job_worker.list_dlq())}


@router.post("/dlq/{dlq_id}/retry")
def retry_dlq_job(
    dlq_id: str,
    background_tasks: BackgroundTasks,
    user: User = Depends(current_user),
) -> dict[str, Any]:
    """Admin: replay a failed job from the DLQ."""
    job = job_worker.retry_dlq_item(dlq_id)
    if not job:
        raise HTTPException(status_code=404, detail="DLQ record not found")
    background_tasks.add_task(job_worker.process_next)
    return {"job_id": job.job_id, "status": job.state, "message": "Job re-enqueued for processing."}


@router.get("/stats")
def get_job_stats(user: User = Depends(current_user)) -> dict[str, Any]:
    """Returns runtime job queue statistics for the current worker engine."""
    return job_worker.get_stats()


# ---------------------------------------------------------------------------
# Trigger processing for a document (background)
# ---------------------------------------------------------------------------

@router.post("/documents/{document_id}/trigger-processing")
def trigger_document_processing(
    document_id: str,
    background_tasks: BackgroundTasks,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Manually triggers (or re-triggers) the full document processing pipeline for a document.
    Safe to call multiple times — idempotent per document.
    """
    doc = db.get(Document, document_id)
    if not doc or doc.user_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    background_tasks.add_task(_run_pipeline_bg, document_id)
    return {
        "document_id": document_id,
        "message": "Document processing pipeline triggered in background.",
        "status": "QUEUED",
    }


def _run_pipeline_bg(document_id: str) -> None:
    """Background task: runs the sync pipeline (no FastAPI context needed for SQLite)."""
    from app.db.session import SessionLocal
    with SessionLocal() as db:
        run_pipeline_for_document(db, document_id)
