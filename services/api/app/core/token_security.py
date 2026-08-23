from __future__ import annotations

import hashlib
import hmac
import secrets


def hash_secret(value: str, *, salt: str | None = None) -> str:
    """Generate salted SHA-256 hash for sensitive authentication tokens and secrets."""
    salt_value = salt or secrets.token_hex(16)
    digest = hashlib.sha256((salt_value + value).encode()).hexdigest()
    return f"{salt_value}${digest}"


def verify_secret(value: str, encoded: str) -> bool:
    """Verify secret against salted SHA-256 hash using constant-time comparison."""
    try:
        salt, expected = encoded.split("$", 1)
    except ValueError:
        return False
    actual = hashlib.sha256((salt + value).encode()).hexdigest()
    return hmac.compare_digest(actual, expected)


def generate_refresh_token() -> str:
    """Generate high-entropy cryptographically secure refresh token string."""
    return secrets.token_urlsafe(48)
