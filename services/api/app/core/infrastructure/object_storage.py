"""
DigiIn Production Infrastructure — Private Encrypted Object Storage Client
Generates short-lived (300s) presigned upload URLs with content-type and size validation (10MB max).
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from typing import Any

ALLOWED_DOCUMENT_TYPES = {"application/pdf", "image/png", "image/jpeg"}
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

class PrivateObjectStorageClient:
    def __init__(self, bucket_name: str = "digiin-prod-documents-encrypted", signing_secret: str = "obj_storage_secret_key_2026"):
        self.bucket_name = bucket_name
        self.signing_secret = signing_secret
        self._stored_objects: dict[str, dict[str, Any]] = {}

    def generate_presigned_upload_url(
        self,
        document_id: str,
        content_type: str,
        file_size_bytes: int,
        ttl_seconds: int = 300
    ) -> dict[str, Any]:
        """Generate presigned upload URL enforcing content-type, size, and expiration."""
        if content_type not in ALLOWED_DOCUMENT_TYPES:
            raise ValueError(f"UNSUPPORTED_MEDIA_TYPE: '{content_type}' is not an authorized document MIME type.")

        if file_size_bytes > MAX_UPLOAD_SIZE_BYTES:
            raise ValueError(f"PAYLOAD_TOO_LARGE: Upload size ({file_size_bytes} bytes) exceeds maximum 10MB limit.")

        object_key = f"docs/{document_id}/{secrets.token_hex(8)}.enc"
        now = time.time()
        expires_at = int(now + ttl_seconds)

        # Generate HMAC-SHA256 signature over upload parameters
        sign_string = f"{self.bucket_name}:{object_key}:{content_type}:{file_size_bytes}:{expires_at}"
        signature = hmac.new(
            self.signing_secret.encode("utf-8"),
            sign_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        upload_url = f"https://storage.digiin.in/{self.bucket_name}/{object_key}?expires={expires_at}&sig={signature}"

        return {
            "uploadUrl": upload_url,
            "objectKey": object_key,
            "bucket": self.bucket_name,
            "expiresAt": expires_at,
            "maxSizeBytes": MAX_UPLOAD_SIZE_BYTES,
            "requiredHeaders": {
                "Content-Type": content_type,
                "x-digiin-kms-encryption": "AES256-GCM",
            }
        }
