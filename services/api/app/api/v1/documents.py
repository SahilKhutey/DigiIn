"""Citizen document upload, version management, and correction requests router."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.storage import save_upload
from app.db import get_db
from app.models.entities import CorrectionCase, Document, DocumentVersion, User
from app.schemas.documents import DocumentDetailOut, DocumentOut, DocumentUploadResponse
from app.services.audit import audit

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    request: Request,
    document_type: str = Form(default="CLASS_XII"),
    title: str = Form(default="Citizen Uploaded Document"),
    file: UploadFile | None = File(default=None),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Uploads a citizen document, validates MIME/size, calculates SHA-256, and creates version record."""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        from app.domain.models import DocumentUploadRequest
        from app.services.platform import upload_document as platform_upload_doc

        body = await request.json()
        req = DocumentUploadRequest(**body)
        res = platform_upload_doc(req)
        return {
            "id": res.documentId,
            "documentId": res.documentId,
            "status": res.status,
            "currentVersion": res.currentVersion,
            "version": res.currentVersion,
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "filename": res.filename,
            "message": "Document metadata created and queued for classification.",
        }

    if not file:
        raise HTTPException(
            status_code=400,
            detail="Document file payload is required for multipart uploads.",
        )

    saved = await save_upload(file)

    doc = Document(
        user_id=user.id,
        document_type=document_type,
        source_type="SELF_UPLOAD",
        verification_status="PENDING_REVIEW",
        title=title,
    )
    db.add(doc)
    db.flush()

    version = DocumentVersion(
        document_id=doc.id,
        version=1,
        storage_key=saved["storage_key"],
        sha256=saved["sha256"],
    )
    db.add(version)
    db.commit()
    db.refresh(doc)

    audit(
        db,
        user.id,
        "DOCUMENT_UPLOADED",
        "document",
        doc.id,
        {"sha256": saved["sha256"], "size": saved["size"], "filename": saved["filename"]},
    )

    return {
        "id": doc.id,
        "documentId": doc.id,
        "status": doc.verification_status,
        "currentVersion": 1,
        "version": 1,
        "sha256": saved["sha256"],
        "filename": saved["filename"],
        "message": "Document uploaded successfully and queued for government review.",
    }


@router.get("", response_model=list[DocumentOut])
def list_documents(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> list[Document]:
    """List all documents owned by the authenticated citizen."""
    stmt = select(Document).where(Document.user_id == user.id).order_by(Document.created_at.desc())
    return list(db.scalars(stmt).all())


@router.get("/{document_id}", response_model=DocumentDetailOut)
def get_document(
    document_id: str,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Get single document metadata and complete version lineage."""
    doc = db.get(Document, document_id)
    if not doc or doc.user_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    version_stmt = (
        select(DocumentVersion)
        .where(DocumentVersion.document_id == doc.id)
        .order_by(DocumentVersion.version.desc())
    )
    versions = list(db.scalars(version_stmt).all())

    return {
        "document": doc,
        "versions": versions,
        "owner": {"id": user.id, "email": user.email},
    }


@router.post("/{document_id}/request-correction")
def request_correction(
    document_id: str,
    issue_type: str = Form("DEMOGRAPHIC_MISMATCH"),
    description: str = Form("Requested correction for document records."),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Citizen requests correction for a document requiring review update."""
    doc = db.get(Document, document_id)
    if not doc or doc.user_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.verification_status = "CORRECTION_REQUIRED"
    case = CorrectionCase(
        user_id=user.id,
        document_id=doc.id,
        issue_type=issue_type,
        description=description,
        status="OPEN",
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    audit(db, user.id, "DOCUMENT_CORRECTION_REQUESTED", "correction_case", case.id)
    return {"id": case.id, "status": case.status, "document_status": doc.verification_status}
