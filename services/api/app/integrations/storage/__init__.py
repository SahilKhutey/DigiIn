from __future__ import annotations

from app.core.config import Settings, get_settings
from app.integrations.storage.base import ObjectStorage, StoredObject
from app.integrations.storage.local import LocalObjectStorage
from app.integrations.storage.s3 import S3ObjectStorage


def get_storage_provider(settings: Settings | None = None) -> ObjectStorage:
    """Factory to resolve configured object storage provider according to environment."""
    current_settings = settings or get_settings()
    if current_settings.environment == "production":
        return S3ObjectStorage()
    return LocalObjectStorage(root=current_settings.object_storage_root)


__all__ = [
    "StoredObject",
    "ObjectStorage",
    "LocalObjectStorage",
    "S3ObjectStorage",
    "get_storage_provider",
]
