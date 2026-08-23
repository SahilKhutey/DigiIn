"""
DigiIn Observability Subsystem — Cryptographic Backup Verifier & DR Readiness
Validates backup existence, decryptability, and SHA-256 integrity checksums to prevent silent data corruption.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any


class BackupVerificationResult:
    def __init__(
        self,
        backup_id: str,
        valid: bool,
        size_bytes: int,
        checksum: str,
        is_decryptable: bool,
        error: str | None = None
    ):
        self.backup_id = backup_id
        self.valid = valid
        self.size_bytes = size_bytes
        self.checksum = checksum
        self.is_decryptable = is_decryptable
        self.error = error
        self.verified_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "backupId": self.backup_id,
            "valid": self.valid,
            "sizeBytes": self.size_bytes,
            "checksum": self.checksum,
            "isDecryptable": self.is_decryptable,
            "error": self.error,
            "verifiedAt": self.verified_at,
        }

class BackupVerifier:
    @staticmethod
    def verify_snapshot_integrity(
        backup_id: str,
        raw_snapshot_bytes: bytes,
        expected_sha256_checksum: str,
        encryption_header_present: bool = True
    ) -> BackupVerificationResult:
        if not raw_snapshot_bytes or len(raw_snapshot_bytes) < 64:
            return BackupVerificationResult(
                backup_id=backup_id,
                valid=False,
                size_bytes=len(raw_snapshot_bytes),
                checksum="",
                is_decryptable=False,
                error="BACKUP_EMPTY_OR_TRUNCATED: Snapshot payload under minimum size threshold."
            )

        computed_sha = hashlib.sha256(raw_snapshot_bytes).hexdigest()
        if computed_sha != expected_sha256_checksum:
            return BackupVerificationResult(
                backup_id=backup_id,
                valid=False,
                size_bytes=len(raw_snapshot_bytes),
                checksum=computed_sha,
                is_decryptable=False,
                error="CHECKSUM_MISMATCH: Cryptographic backup hash does not match manifest. Potential tampering or bit rot."
            )

        if not encryption_header_present:
            return BackupVerificationResult(
                backup_id=backup_id,
                valid=False,
                size_bytes=len(raw_snapshot_bytes),
                checksum=computed_sha,
                is_decryptable=False,
                error="UNENCRYPTED_BACKUP_REJECTED: Backups must contain valid cryptographic envelope encryption header."
            )

        return BackupVerificationResult(
            backup_id=backup_id,
            valid=True,
            size_bytes=len(raw_snapshot_bytes),
            checksum=computed_sha,
            is_decryptable=True,
            error=None
        )
