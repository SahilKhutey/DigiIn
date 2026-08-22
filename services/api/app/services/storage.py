"""Object storage adapter for document storage, integrity hashing, and validation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "text/plain",
}


class StorageAdapter:
    """Manages document file storage and cryptographic hash generation."""

    def __init__(self, base_storage_dir: str = "./data/storage") -> None:
        self.base_dir = Path(base_storage_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, filename: str, file_bytes: bytes, mime_type: str | None = None) -> None:
        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            raise ValueError(f"File size exceeds maximum permitted limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB")
        if mime_type and mime_type not in ALLOWED_MIME_TYPES:
            raise ValueError(f"Unsupported file MIME type: {mime_type}")

    def store_file(self, document_id: str, filename: str, file_bytes: bytes) -> dict[str, Any]:
        self.validate_file(filename, file_bytes)
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        ext = Path(filename).suffix or ".bin"
        storage_key = f"{document_id}_{sha256[:12]}{ext}"
        target_path = self.base_dir / storage_key

        with open(target_path, "wb") as f:
            f.write(file_bytes)

        return {
            "storage_key": storage_key,
            "sha256": sha256,
            "size_bytes": len(file_bytes),
            "storage_path": str(target_path),
        }

    def retrieve_file(self, storage_key: str) -> bytes | None:
        target_path = self.base_dir / storage_key
        if not target_path.exists():
            return None
        with open(target_path, "rb") as f:
            return f.read()


storage_adapter = StorageAdapter()
