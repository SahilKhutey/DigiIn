"""Phase 8.3 — Key Management Registry.

Per-purpose cryptographic key lifecycle management.

Key purposes are strictly separated:
  AUTH_SIGNING        ≠  CREDENTIAL_SIGNING
  CREDENTIAL_SIGNING  ≠  DOCUMENT_ENCRYPTION
  DOCUMENT_ENCRYPTION ≠  WEBHOOK_VERIFICATION
  WEBHOOK_VERIFICATION ≠ FIELD_ENCRYPTION

Key lifecycle states:
  ACTIVE → VERIFY_ONLY → SCHEDULED_ROTATION → REVOKED

Key records carry full lifecycle metadata:
  key_id | purpose | algorithm | created_at | activated_at | expires_at | status | rotation_version
"""

from __future__ import annotations

import hashlib
import os
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class KeyPurpose(StrEnum):
    AUTH_SIGNING = "auth_signing"
    CREDENTIAL_SIGNING = "credential_signing"
    DOCUMENT_ENCRYPTION = "document_encryption"
    WEBHOOK_VERIFICATION = "webhook_verification"
    FIELD_ENCRYPTION = "field_encryption"


class KeyStatus(StrEnum):
    ACTIVE = "ACTIVE"
    VERIFY_ONLY = "VERIFY_ONLY"          # Can verify old signatures but not sign new ones
    SCHEDULED_ROTATION = "SCHEDULED_ROTATION"
    REVOKED = "REVOKED"


class KeyAlgorithm(StrEnum):
    HMAC_SHA256 = "HMAC-SHA256"
    AES_256_GCM = "AES-256-GCM"
    ED25519 = "Ed25519"
    RS256 = "RS256"


# ---------------------------------------------------------------------------
# Key Record
# ---------------------------------------------------------------------------


@dataclass
class KeyRecord:
    key_id: str
    purpose: KeyPurpose
    algorithm: KeyAlgorithm
    status: KeyStatus
    rotation_version: int
    created_at: datetime
    activated_at: datetime
    expires_at: datetime | None
    _raw_key: bytes = field(default=b"", repr=False)  # Never surfaces in repr/logs

    def is_active(self) -> bool:
        if self.status != KeyStatus.ACTIVE:
            return False
        if self.expires_at and datetime.now(UTC) > self.expires_at:
            return False
        return True

    def is_verifiable(self) -> bool:
        """Key can still verify signatures even if no longer signing."""
        return self.status in (KeyStatus.ACTIVE, KeyStatus.VERIFY_ONLY)

    def days_until_expiry(self) -> int | None:
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.now(UTC)
        return max(0, delta.days)

    def to_public_dict(self) -> dict[str, Any]:
        """Safe public representation — never exposes raw key material."""
        return {
            "key_id": self.key_id,
            "purpose": self.purpose.value,
            "algorithm": self.algorithm.value,
            "status": self.status.value,
            "rotation_version": self.rotation_version,
            "created_at": self.created_at.isoformat(),
            "activated_at": self.activated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "days_until_expiry": self.days_until_expiry(),
        }


# ---------------------------------------------------------------------------
# Key Registry
# ---------------------------------------------------------------------------


class KeyRegistry:
    """
    Central registry managing per-purpose cryptographic key lifecycle.

    In development: deterministic keys derived from DIGIIN_MASTER_SECRET.
    In production:  integrate with HSM / AWS KMS / Google Cloud KMS.
    """

    # Default key rotation periods per purpose
    _ROTATION_PERIODS: dict[KeyPurpose, int] = {
        KeyPurpose.AUTH_SIGNING: 90,           # days
        KeyPurpose.CREDENTIAL_SIGNING: 365,
        KeyPurpose.DOCUMENT_ENCRYPTION: 730,
        KeyPurpose.WEBHOOK_VERIFICATION: 180,
        KeyPurpose.FIELD_ENCRYPTION: 730,
    }

    def __init__(self) -> None:
        self._keys: dict[str, KeyRecord] = {}          # key_id → KeyRecord
        self._active: dict[KeyPurpose, str] = {}        # purpose → active key_id
        self._master_secret = os.environ.get(
            "DIGIIN_MASTER_SECRET", "digiin-master-secret-dev-only-2026"
        ).encode()
        self._bootstrap()

    # ── Bootstrap ────────────────────────────────────────────────────────────

    def _bootstrap(self) -> None:
        """Create one deterministic active key per purpose for development."""
        for purpose in KeyPurpose:
            key_id = f"dev-{purpose.value}-v1"
            raw = hashlib.sha256(self._master_secret + purpose.value.encode()).digest()
            rotation_days = self._ROTATION_PERIODS[purpose]
            now = datetime.now(UTC)
            record = KeyRecord(
                key_id=key_id,
                purpose=purpose,
                algorithm=self._default_algorithm(purpose),
                status=KeyStatus.ACTIVE,
                rotation_version=1,
                created_at=now,
                activated_at=now,
                expires_at=now + timedelta(days=rotation_days),
                _raw_key=raw,
            )
            self._keys[key_id] = record
            self._active[purpose] = key_id

    def _default_algorithm(self, purpose: KeyPurpose) -> KeyAlgorithm:
        return {
            KeyPurpose.AUTH_SIGNING: KeyAlgorithm.HMAC_SHA256,
            KeyPurpose.CREDENTIAL_SIGNING: KeyAlgorithm.ED25519,
            KeyPurpose.DOCUMENT_ENCRYPTION: KeyAlgorithm.AES_256_GCM,
            KeyPurpose.WEBHOOK_VERIFICATION: KeyAlgorithm.HMAC_SHA256,
            KeyPurpose.FIELD_ENCRYPTION: KeyAlgorithm.AES_256_GCM,
        }[purpose]

    # ── Lookups ────────────────────────────────────────────────────────────

    def get_active(self, purpose: KeyPurpose) -> KeyRecord:
        """Return the currently active key for a purpose. Raises if none."""
        key_id = self._active.get(purpose)
        if not key_id:
            raise KeyError(f"No active key for purpose '{purpose.value}'")
        record = self._keys[key_id]
        if not record.is_active():
            raise RuntimeError(
                f"Active key '{key_id}' for purpose '{purpose.value}' is expired or revoked"
            )
        return record

    def get_by_id(self, key_id: str) -> KeyRecord | None:
        return self._keys.get(key_id)

    def get_raw_key(self, key_id: str) -> bytes:
        """Return raw key material. NEVER log this value."""
        record = self._keys.get(key_id)
        if not record:
            raise KeyError(f"Key '{key_id}' not found")
        if record.status == KeyStatus.REVOKED:
            raise PermissionError(f"Key '{key_id}' is REVOKED and cannot be used")
        return record._raw_key  # noqa: SLF001

    def get_active_raw(self, purpose: KeyPurpose) -> tuple[str, bytes]:
        """Return (key_id, raw_key) for the active key of a purpose."""
        record = self.get_active(purpose)
        return record.key_id, record._raw_key  # noqa: SLF001

    # ── Key rotation ────────────────────────────────────────────────────────

    def rotate(self, purpose: KeyPurpose) -> KeyRecord:
        """
        Rotate the active key for a purpose.
        Old key transitions to VERIFY_ONLY so existing signatures remain valid.
        """
        old_id = self._active.get(purpose)
        if old_id and old_id in self._keys:
            old = self._keys[old_id]
            old.status = KeyStatus.VERIFY_ONLY

        # Determine next rotation version
        existing_versions = [
            r.rotation_version
            for r in self._keys.values()
            if r.purpose == purpose
        ]
        next_version = max(existing_versions, default=0) + 1

        new_raw = os.urandom(32)
        new_id = f"key-{purpose.value}-v{next_version}-{uuid.uuid4().hex[:8]}"
        now = datetime.now(UTC)
        rotation_days = self._ROTATION_PERIODS[purpose]
        new_record = KeyRecord(
            key_id=new_id,
            purpose=purpose,
            algorithm=self._default_algorithm(purpose),
            status=KeyStatus.ACTIVE,
            rotation_version=next_version,
            created_at=now,
            activated_at=now,
            expires_at=now + timedelta(days=rotation_days),
            _raw_key=new_raw,
        )
        self._keys[new_id] = new_record
        self._active[purpose] = new_id
        return new_record

    def revoke(self, key_id: str) -> None:
        record = self._keys.get(key_id)
        if not record:
            raise KeyError(f"Key '{key_id}' not found")
        record.status = KeyStatus.REVOKED
        # If it was the active key, clear active pointer
        if self._active.get(record.purpose) == key_id:
            del self._active[record.purpose]

    def list_keys(self, purpose: KeyPurpose | None = None) -> list[dict[str, Any]]:
        records = self._keys.values()
        if purpose:
            records = [r for r in records if r.purpose == purpose]  # type: ignore[assignment]
        return [r.to_public_dict() for r in records]

    def needs_rotation(self, purpose: KeyPurpose, warning_days: int = 30) -> bool:
        """Return True if the active key expires within warning_days."""
        try:
            record = self.get_active(purpose)
            days = record.days_until_expiry()
            return days is not None and days <= warning_days
        except (KeyError, RuntimeError):
            return True


# ---------------------------------------------------------------------------
# Module singleton
# ---------------------------------------------------------------------------

key_registry = KeyRegistry()
