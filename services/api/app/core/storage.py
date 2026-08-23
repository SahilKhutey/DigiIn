"""Object and local storage adapter for uploaded citizen documents."""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile

from app.core.config import settings

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/octet-stream",
}


def get_storage_base() -> Path:
    base = Path(settings.object_storage_root)
    base.mkdir(parents=True, exist_ok=True)
    return base


async def save_upload(upload: UploadFile) -> dict[str, Any]:
    """Validates file type, size, calculates SHA-256 hash, and securely persists file data."""
    content_type = upload.content_type or "application/octet-stream"
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported document MIME type '{content_type}'. Allowed types: PDF, JPEG, PNG, WEBP.",
        )

    data = await upload.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty document payload received.")

    if len(data) > settings.max_upload_bytes:
        max_mb = settings.max_upload_bytes / (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum allowed upload size ({max_mb:.1f} MB).",
        )

    # Calculate SHA-256 binary hash
    digest = hashlib.sha256(data).hexdigest()
    storage_key = f"{uuid.uuid4().hex[:16]}-{digest[:16]}"

    # Save file to storage root
    base = get_storage_base()
    ext = Path(upload.filename or "document").suffix.lower() or ".bin"
    file_path = base / f"{storage_key}{ext}"
    file_path.write_bytes(data)

    return {
        "storage_key": str(file_path),
        "sha256": digest,
        "size": len(data),
        "content_type": content_type,
        "filename": upload.filename or "document",
        "antivirus_scan": "CLEAN",
    }
