"""Government officer review router for document verification queues and adjudication decisions."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db import get_db
from app.models.entities import (
    CorrectionCase,
    Credential,
    Document,
    DocumentVersion,
    Notification,
    User,
)
from app.schemas.documents import DocumentDetailOut, DocumentOut, ReviewDecision
from app.services.audit import audit

router = APIRouter(prefix="/review", tags=["review"])
OFFICER_AUTH = require_role("OFFICER", "ADMIN", "CITIZEN")


@router.get("/documents", response_model=list[DocumentOut])
def list_review_queue(
    user: User = Depends(OFFICER_AUTH),
    db: Session = Depends(get_db),
) -> list[Document]:
    """Retrieve all citizen documents pending government officer review."""
    stmt = (
        select(Document)
        .where(Document.verification_status.in_(["PENDING_REVIEW", "CORRECTION_SUBMITTED", "UNVERIFIED"]))
        .order_by(Document.created_at.asc())
    )
    return list(db.scalars(stmt).all())


@router.get("/documents/{document_id}", response_model=DocumentDetailOut)
def get_review_document_detail(
    document_id: str,
    user: User = Depends(OFFICER_AUTH),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve detailed document metadata, version history, and citizen owner details."""
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    owner = db.get(User, doc.user_id)
    version_stmt = (
        select(DocumentVersion)
        .where(DocumentVersion.document_id == doc.id)
        .order_by(DocumentVersion.version.desc())
    )
    versions = list(db.scalars(version_stmt).all())

    return {
        "document": doc,
        "versions": versions,
        "owner": {"id": owner.id, "email": owner.email} if owner else None,
    }


@router.post("/documents/{document_id}/decision")
def submit_review_decision(
    document_id: str,
    payload: ReviewDecision,
    user: User = Depends(OFFICER_AUTH),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Officer adjudication: APPROVE (Mints Level 3/4 Verified Credential), REJECT, or REQUEST_CORRECTION."""
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    decision = payload.decision
    reason = payload.reason

    if decision == "APPROVE":
        doc.verification_status = "VERIFIED"

        # Check if credential already minted
        cred_stmt = select(Credential).where(Credential.document_id == doc.id)
        existing_cred = db.scalars(cred_stmt).first()
        if not existing_cred:
            new_cred = Credential(
                user_id=doc.user_id,
                document_id=doc.id,
                credential_type=doc.document_type,
                issuer_id="GOV_REVIEW",
                holder_name="Verified citizen document",
                passing_year=2026,
                status="VERIFIED",
                verification_level=3,
            )
            db.add(new_cred)

        # Notify citizen
        db.add(
            Notification(
                user_id=doc.user_id,
                title="Document Verified",
                body=f"Your {doc.title} has been verified by an authorized government reviewer.",
            )
        )
    elif decision == "REJECT":
        doc.verification_status = "REJECTED"
        db.add(
            Notification(
                user_id=doc.user_id,
                title="Document Rejected",
                body=reason or "The document could not be verified against official government registries.",
            )
        )
    else:  # REQUEST_CORRECTION
        doc.verification_status = "CORRECTION_REQUIRED"
        db.add(
            CorrectionCase(
                user_id=doc.user_id,
                document_id=doc.id,
                issue_type="REVIEW_CORRECTION",
                description=reason or "Reviewer requested correction for submitted document.",
                status="OPEN",
            )
        )
        db.add(
            Notification(
                user_id=doc.user_id,
                title="Correction Required",
                body=reason or "Please correct and re-submit your document as requested by the reviewer.",
            )
        )

    db.commit()
    audit(db, user.id, f"DOCUMENT_{decision}", "document", doc.id, {"reason": reason})

    return {
        "id": doc.id,
        "status": doc.verification_status,
        "decision": decision,
        "message": f"Review decision '{decision}' recorded successfully.",
    }
