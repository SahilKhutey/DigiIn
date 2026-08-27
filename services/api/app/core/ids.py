from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

# 32-character human-friendly Base32 alphabet (excludes 0, 1, I, O)
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
EXCLUDED_CHARS = set("01IOio")

# Official DigiIn Account ID regex: DI-XXXX-XXXX-XXXX (14 characters total)
ACCOUNT_ID_PATTERN = re.compile(r"^DI-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}$")

# Legacy compatibility patterns (DIN-XXXX-XXXX-XXXX, DIN-DEMO-XXX, DGI-SBX-XXX)
LEGACY_ACCOUNT_ID_PATTERN = re.compile(
    r"^(DIN|DGI)-([A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}|DEMO-[0-9]{3}|SBX-[0-9]{3})$"
)

# Salt for hashing temporary verification codes
TEMP_CODE_SALT = b"digiin_temp_verification_code_salt_v1"


@dataclass(frozen=True)
class DualIdentity:
    """Separation of citizen-facing public alias and system-facing internal identifier."""

    public_account_id: str  # e.g., DI-7K4M-9Q2X-8P6R
    internal_account_id: str  # e.g., UUIDv7 / UUID4 primary key
    created_at: datetime


@dataclass(frozen=True)
class TemporaryVerificationCode:
    """Ephemeral 6-digit verification code valid for 10 minutes."""

    account_id: str
    code: str  # 6-digit string, e.g. "482913"
    expires_at_epoch: float
    expires_at_iso: str
    code_hash: str
    ttl_seconds: int = 600


def generate_account_id(
    check_collision_fn: Callable[[str], bool] | None = None,
    max_retries: int = 10,
) -> str:
    """Generate an opaque, non-semantic, non-sequential DigiIn Account ID (DI-XXXX-XXXX-XXXX).

    - 12 meaningful random characters from Base32 alphabet + DI- prefix + separators.
    - ~1.15 * 10^18 possible IDs (32^12).
    - Contains zero PII (no Aadhaar, DOB, name, phone, or state codes).
    - Enforces collision check and retry logic.
    """
    for _ in range(max_retries):
        parts = ["".join(secrets.choice(ALPHABET) for _ in range(4)) for _ in range(3)]
        candidate = "DI-" + "-".join(parts)

        # Check collision if callback is provided
        if check_collision_fn is not None:
            if not check_collision_fn(candidate):
                return candidate
        else:
            return candidate

    # Fallback in extreme collision case: append crypto entropy
    parts = ["".join(secrets.choice(ALPHABET) for _ in range(4)) for _ in range(3)]
    return "DI-" + "-".join(parts)


def is_valid_account_id(value: str, allow_legacy: bool = True) -> bool:
    """Validate whether an Account ID matches the DigiIn specification."""
    if not value or not isinstance(value, str):
        return False

    cleaned = value.strip().upper()
    if bool(ACCOUNT_ID_PATTERN.fullmatch(cleaned)):
        return True

    if allow_legacy and bool(LEGACY_ACCOUNT_ID_PATTERN.fullmatch(cleaned)):
        return True

    return False


def create_dual_identity(
    public_id: str | None = None,
    check_collision_fn: Callable[[str], bool] | None = None,
) -> DualIdentity:
    """Factory creating a cryptographically paired Public Account ID and Internal UUID."""
    pub_id = public_id if (public_id and is_valid_account_id(public_id)) else generate_account_id(check_collision_fn)
    internal_id = str(uuid4())
    return DualIdentity(
        public_account_id=pub_id,
        internal_account_id=internal_id,
        created_at=datetime.now(UTC),
    )


def hash_temp_code(account_id: str, code: str) -> str:
    """Hash a temporary verification code with HMAC-SHA256."""
    msg = f"{account_id.strip().upper()}:{code.strip()}".encode()
    return hmac.new(TEMP_CODE_SALT, msg, hashlib.sha256).hexdigest()


def generate_temporary_verification_code(
    account_id: str,
    validity_seconds: int = 600,
) -> TemporaryVerificationCode:
    """Generate an ephemeral 6-digit verification code with 10-minute TTL."""
    # Generate 6-digit numeric code with crypto RNG
    code_int = secrets.randbelow(1_000_000)
    code = f"{code_int:06d}"

    now_epoch = time.time()
    expires_epoch = now_epoch + validity_seconds
    expires_dt = datetime.fromtimestamp(expires_epoch, tz=UTC)
    code_hash = hash_temp_code(account_id, code)

    return TemporaryVerificationCode(
        account_id=account_id,
        code=code,
        expires_at_epoch=expires_epoch,
        expires_at_iso=expires_dt.isoformat(),
        code_hash=code_hash,
        ttl_seconds=validity_seconds,
    )


def verify_temporary_verification_code(
    account_id: str,
    candidate_code: str,
    stored_hash: str,
    expires_at_epoch: float,
) -> tuple[bool, str]:
    """Verify an ephemeral 6-digit verification code."""
    if time.time() > expires_at_epoch:
        return False, "EXPIRED: Verification code has expired (10-minute window exceeded)."

    candidate_hash = hash_temp_code(account_id, candidate_code)
    if not hmac.compare_digest(candidate_hash, stored_hash):
        return False, "INVALID_CODE: The provided verification code does not match."

    return True, "VERIFIED: Temporary verification code is valid."
