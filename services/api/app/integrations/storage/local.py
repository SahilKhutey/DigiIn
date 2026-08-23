from __future__ import annotations

import hashlib
import os
import secrets
from pathlib import Path
from typing import BinaryIO

from app.integrations.storage.base import ObjectStorage, StoredObject


class LocalObjectStorage(ObjectStorage):
    """Development object storage.

    Files are addressed by generated object IDs, never by user filenames.
    Replace with an S3/KMS-backed adapter for production.
    """

    def __init__(self, root: str):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve_safe_path(self, object_id: str) -> Path:
        """Resolve path and guard against directory traversal attacks."""
        cleaned = os.path.basename(object_id)
        target = (self.root / cleaned).resolve()
        if not target.is_relative_to(self.root):
            raise ValueError("Invalid object path traversal attempt")
        return target

    def put(
        self,
        stream: BinaryIO,
        *,
        content_type: str,
        expected_hash: str | None = None,
    ) -> StoredObject:
        object_id = secrets.token_hex(16)
        target = self._resolve_safe_path(object_id)
        digest = hashlib.sha256()
        size = 0

        with target.open("wb") as destination:
            while chunk := stream.read(1024 * 1024):
                size += len(chunk)
                digest.update(chunk)
                destination.write(chunk)

        content_hash = digest.hexdigest()
        if expected_hash and expected_hash.lower() != content_hash.lower():
            target.unlink(missing_ok=True)
            raise ValueError("content hash mismatch")

        return StoredObject(
            object_id=object_id,
            content_hash=content_hash,
            size_bytes=size,
            content_type=content_type,
        )

    def open(self, object_id: str) -> BinaryIO:
        path = self._resolve_safe_path(object_id)
        if not path.exists():
            raise FileNotFoundError(object_id)
        return path.open("rb")

    def delete(self, object_id: str) -> None:
        try:
            path = self._resolve_safe_path(object_id)
            path.unlink(missing_ok=True)
        except ValueError:
            pass
