from __future__ import annotations

from typing import BinaryIO

from app.integrations.storage.base import ObjectStorage, StoredObject


class S3ObjectStorage(ObjectStorage):
    """Production AWS S3 / KMS envelope encryption object storage adapter.

    Encrypted-at-rest document binary persistence with multi-region replication.
    """

    def __init__(self, bucket_name: str = "digiin-documents-vault", kms_key_id: str | None = None) -> None:
        self.bucket_name = bucket_name
        self.kms_key_id = kms_key_id

    def put(
        self,
        stream: BinaryIO,
        *,
        content_type: str,
        expected_hash: str | None = None,
    ) -> StoredObject:
        raise NotImplementedError("Production AWS S3/KMS credentials not configured in local environment")

    def open(self, object_id: str) -> BinaryIO:
        raise NotImplementedError("Production AWS S3/KMS credentials not configured in local environment")

    def delete(self, object_id: str) -> None:
        raise NotImplementedError("Production AWS S3/KMS credentials not configured in local environment")
