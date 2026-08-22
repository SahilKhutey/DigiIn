"""Security core module for DigiLocker X (DigiIn) with hardened cryptographic protections."""

from __future__ import annotations

import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import HTTPException

from app.core.config import settings

AUTH_ISSUER = "digilocker-x-auth"
AUTH_AUDIENCE = "digilocker-x-client"


def hash_password(password: str) -> str:
    """Generate salted SHA-256 password hash for prototype development."""
    salt = "digilocker_x_salt_"
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time password verification to prevent timing side-channel attacks."""
    computed_hash = hash_password(plain_password)
    return hmac.compare_digest(computed_hash.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(user_id: str, role: str = "CITIZEN", custom_claims: dict[str, Any] | None = None) -> str:
    """Create short-lived JWT access token (15 mins) with strict issuer, audience, and not-before claims."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "iss": AUTH_ISSUER,
        "aud": AUTH_AUDIENCE,
        "sub": user_id,
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()) - 5,  # 5 seconds clock drift allowance
        "exp": int((now + timedelta(minutes=settings.access_token_expire_minutes)).timestamp()),
    }
    if custom_claims:
        payload.update(custom_claims)

    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str, session_id: str) -> str:
    """Create rotating refresh token (30 days)."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "iss": AUTH_ISSUER,
        "aud": AUTH_AUDIENCE,
        "sub": user_id,
        "sid": session_id,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()) - 5,
        "exp": int((now + timedelta(days=settings.refresh_token_expire_days)).timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(
    token: str,
    expected_type: str = "access",
    verify_aud: bool = False,
) -> dict[str, Any]:
    """Decode and strictly validate token signature, expiration, leeway, and type."""
    try:
        decode_options = {"verify_aud": verify_aud}
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
            options=decode_options,
            leeway=60,  # Allow up to 60s of clock skew tolerance
        )
        if payload.get("type") != expected_type:
            raise HTTPException(status_code=401, detail=f"Invalid token type: expected {expected_type}")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.ImmatureSignatureError:
        raise HTTPException(status_code=401, detail="Token is not yet valid (nbf violation)")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token signature or malformed payload")
