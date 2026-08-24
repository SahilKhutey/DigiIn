"""Phase 9.3 — Multi-Tier Object Storage & Integrity Verification.

Provides an object storage layer with cryptographic SHA-256 integrity checks,
retention tracking, and a bounded cache layer for fast ephemeral challenge/nonce validation.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any


class StorageIntegrityError(Exception):
    """Raised when an object's decrypted/stored binary fails SHA-256 verification."""


@dataclass
class StoredObject:
    object_id: str
    document_id: str
    version: int
    content_hash: str  # SHA-256 hex digest
    encrypted_size: int
    media_type: str
    storage_key: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    retention_until: datetime = field(
        default_factory=lambda: datetime.now(UTC) + timedelta(days=365 * 7)
    )
    metadata: dict[str, Any] = field(default_factory=dict)


class ObjectStorageService:
    """Object storage service with integrity auditing and envelope storage management."""

    def __init__(self) -> None:
        self._objects: dict[str, StoredObject] = {}
        self._blobs: dict[str, bytes] = {}  # storage_key -> raw/encrypted bytes

    def put_object(
        self,
        document_id: str,
        content: bytes,
        media_type: str = "application/pdf",
        version: int = 1,
        retention_days: int = 365 * 7,
        metadata: dict[str, Any] | None = None,
    ) -> StoredObject:
        """Stores a new object and computes its authoritative SHA-256 hash."""
        object_id = f"obj_{uuid.uuid4().hex[:12]}"
        content_hash = hashlib.sha256(content).hexdigest()
        storage_key = f"vault/{document_id}/v{version}/{object_id}"

        stored = StoredObject(
            object_id=object_id,
            document_id=document_id,
            version=version,
            content_hash=content_hash,
            encrypted_size=len(content),
            media_type=media_type,
            storage_key=storage_key,
            created_at=datetime.now(UTC),
            retention_until=datetime.now(UTC) + timedelta(days=retention_days),
            metadata=metadata or {},
        )

        self._objects[object_id] = stored
        self._blobs[storage_key] = content
        return stored

    def get_object(self, object_id: str) -> tuple[StoredObject, bytes]:
        """Retrieves an object and cryptographically verifies its content hash integrity."""
        record = self._objects.get(object_id)
        if not record:
            raise KeyError(f"Object not found: {object_id}")

        blob = self._blobs.get(record.storage_key)
        if blob is None:
            raise KeyError(f"Binary blob missing for storage key: {record.storage_key}")

        # Cryptographic integrity check
        computed_hash = hashlib.sha256(blob).hexdigest()
        if computed_hash != record.content_hash:
            raise StorageIntegrityError(
                f"Storage integrity failure for object {object_id}: "
                f"computed hash {computed_hash[:16]}... does not match recorded {record.content_hash[:16]}..."
            )

        return record, blob

    def delete_object(self, object_id: str) -> bool:
        """Securely deletes an object from storage."""
        record = self._objects.pop(object_id, None)
        if record:
            self._blobs.pop(record.storage_key, None)
            return True
        return False

    def list_document_versions(self, document_id: str) -> list[StoredObject]:
        """Lists all stored versions for a given document."""
        return [obj for obj in self._objects.values() if obj.document_id == document_id]

    def count(self) -> int:
        return len(self._objects)


class BoundedCache:
    """In-memory Redis-compatible key-value cache with bounded capacity and TTL."""

    def __init__(self, max_items: int = 10000) -> None:
        self.max_items = max_items
        self._cache: dict[str, tuple[Any, float]] = {}  # key -> (value, expires_at)
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        now = datetime.now(UTC).timestamp()
        if key in self._cache:
            val, expires_at = self._cache[key]
            if now <= expires_at:
                self._hits += 1
                return val
            del self._cache[key]

        self._misses += 1
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        if len(self._cache) >= self.max_items:
            # Evict 10% oldest items
            items_to_remove = max(1, len(self._cache) // 10)
            sorted_keys = sorted(self._cache.keys(), key=lambda k: self._cache[k][1])
            for k in sorted_keys[:items_to_remove]:
                del self._cache[k]

        expires_at = datetime.now(UTC).timestamp() + ttl_seconds
        self._cache[key] = (value, expires_at)

    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def get_hit_rate(self) -> float:
        total = self._hits + self._misses
        return (self._hits / total) if total > 0 else 1.0


# Global singleton instances
object_storage = ObjectStorageService()
ephemeral_cache = BoundedCache()
