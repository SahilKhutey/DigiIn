"""Verification Intelligence API router exposing job pipeline, OCR extraction, evidence graph, and risk scoring."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db import get_db
from app.models.entities import (
    Document,
    DocumentExtraction,
    DocumentJob,
    DocumentMatch,
    RiskAssessment,
    User,
    VerificationEvidence,
)
from app.services.job_queue import create_document_pipeline_jobs, run_pipeline_for_document

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.post("/documents/{document_id}/process")
def process_document_pipeline(
    document_id: str,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Trigger the asynchronous verification intelligence pipeline for a document."""
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    jobs = list(db.scalars(select(DocumentJob).where(DocumentJob.document_id == document_id)).all())
    if not jobs:
        create_document_pipeline_jobs(db, document_id)

    result = run_pipeline_for_document(db, document_id)
    return result


@router.get("/documents/{document_id}/pipeline")
def get_document_pipeline_jobs(
    document_id: str,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve the status of all asynchronous processing jobs for a document."""
    jobs = list(
        db.scalars(
            select(DocumentJob)
            .where(DocumentJob.document_id == document_id)
            .order_by(DocumentJob.priority.asc())
        ).all()
    )
    return {
        "document_id": document_id,
        "total_jobs": len(jobs),
        "jobs": [
            {
                "id": j.id,
                "job_type": j.job_type,
                "status": j.status,
                "priority": j.priority,
                "attempts": j.attempts,
                "started_at": j.started_at,
                "completed_at": j.completed_at,
                "error_message": j.error_message,
            }
            for j in jobs
        ],
    }


@router.get("/documents/{document_id}/evidence")
def get_verification_evidence_graph(
    document_id: str,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve the complete verification evidence graph for a document."""
    evidence_list = list(
        db.scalars(
            select(VerificationEvidence)
            .where(VerificationEvidence.document_id == document_id)
            .order_by(VerificationEvidence.created_at.asc())
        ).all()
    )
    return {
        "document_id": document_id,
        "evidence_count": len(evidence_list),
        "evidence": [
            {
                "id": ev.id,
                "evidence_type": ev.evidence_type,
                "source": ev.source,
                "reference": ev.reference,
                "result": ev.result,
                "confidence": ev.confidence,
                "metadata": json.loads(ev.metadata_json) if ev.metadata_json else {},
                "created_at": ev.created_at,
            }
            for ev in evidence_list
        ],
    }


@router.get("/documents/{document_id}/risk")
def get_document_risk_assessment(
    document_id: str,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve multi-factor risk assessment for a document."""
    risk = db.scalars(
        select(RiskAssessment)
        .where(RiskAssessment.document_id == document_id)
        .order_by(RiskAssessment.created_at.desc())
    ).first()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk assessment not found for document")

    return {
        "document_id": document_id,
        "score": risk.score,
        "level": risk.level,
        "factors": json.loads(risk.factors_json) if risk.factors_json else {},
        "created_at": risk.created_at,
    }


@router.get("/documents/{document_id}/extraction")
def get_document_extraction(
    document_id: str,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve OCR extraction fields and classification details."""
    ext = db.scalars(
        select(DocumentExtraction)
        .where(DocumentExtraction.document_id == document_id)
        .order_by(DocumentExtraction.version.desc())
    ).first()
    if not ext:
        raise HTTPException(status_code=404, detail="Extraction not found for document")

    match = db.scalars(
        select(DocumentMatch)
        .where(DocumentMatch.document_id == document_id)
        .order_by(DocumentMatch.created_at.desc())
    ).first()

    return {
        "document_id": document_id,
        "version": ext.version,
        "provider": ext.provider,
        "classification": {
            "type": ext.classification_type,
            "confidence": ext.classification_confidence,
        },
        "extracted_fields": json.loads(ext.extracted_fields_json) if ext.extracted_fields_json else {},
        "duplicate_detection": {
            "match_type": match.match_type if match else "NO_MATCH",
            "similarity_score": match.similarity_score if match else 0.0,
            "details": json.loads(match.details_json) if match and match.details_json else {},
        },
        "created_at": ext.created_at,
    }
