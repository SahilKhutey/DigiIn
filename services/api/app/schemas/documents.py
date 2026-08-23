"""Pydantic schemas for citizen document uploads, versioning, and government review."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class ReviewDecision(BaseModel):
    decision: Literal["APPROVE", "REJECT", "REQUEST_CORRECTION"]
    reason: str | None = None


class DocumentUploadResponse(BaseModel):
    id: str
    documentId: str | None = None
    status: str
    currentVersion: int = 1
    version: int = 1
    sha256: str
    filename: str
    message: str = "Document uploaded successfully and queued for government review."


class DocumentVersionOut(BaseModel):
    id: str
    document_id: str
    version: int
    storage_key: str
    sha256: str
    created_at: datetime


class DocumentOut(BaseModel):
    id: str
    user_id: str
    document_type: str
    source_type: str
    verification_status: str
    title: str
    created_at: datetime


class DocumentDetailOut(BaseModel):
    document: DocumentOut
    versions: list[DocumentVersionOut]
    owner: dict[str, Any] | None = None
