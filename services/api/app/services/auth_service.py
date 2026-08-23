"""Hardened Sovereign Identity, Challenge, and Session Management Service for Phase 3."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import app.db.repository as repo
from app.core.config import get_settings
from app.core.ids import generate_account_id
from app.core.security import create_access_token
from app.core.token_security import generate_refresh_token, hash_secret, verify_secret
from app.domain.auth_models import (
    AuthChallengeRecord,
    DigiInAccountRecord,
    IdentityClaimRecord,
    SecurityEventRecord,
    SessionRecord,
)

MAX_OTP_ATTEMPTS = 3
OTP_EXPIRY_MINUTES = 5
REFRESH_TOKEN_EXPIRY_DAYS = 30


def _to_utc(dt: datetime | None) -> datetime:
    if dt is None:
        return datetime.now(UTC)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def get_or_create_account(phone_number: str, role: str = "CITIZEN") -> DigiInAccountRecord:
    """Resolve existing account by phone or provision a new sovereign DigiInAccount."""
    clean_phone = phone_number.strip()
    account = repo.get_account_by_phone(clean_phone)
    if account is not None:
        return account

    account_id = generate_account_id()
    account_pk = f"acc_{uuid4().hex[:12]}"
    now = datetime.now(UTC)

    new_acc = DigiInAccountRecord(
        id=account_pk,
        account_id=account_id,
        phone_number=clean_phone,
        role=role,
        status="ACTIVE",
        created_at=now,
        updated_at=now,
    )
    return repo.save_account(new_acc)


def create_auth_challenge(
    phone_number: str,
    channel: str = "SMS",
    request_id: str | None = None,
) -> tuple[str, str, str]:
    """Issue a short-lived authentication challenge with salted OTP hash."""
    settings = get_settings()
    account = get_or_create_account(phone_number)
    now = datetime.now(UTC)

    challenge_id = f"ch_{uuid4().hex[:12]}"
    otp_plain = "123456" if settings.is_demo or settings.environment in {"development", "test"} else f"{uuid4().int % 900000 + 100000}"
    challenge_hash = hash_secret(otp_plain)

    challenge = AuthChallengeRecord(
        challenge_id=challenge_id,
        account_id=account.account_id,
        channel=channel,
        challenge_hash=challenge_hash,
        expires_at=now + timedelta(minutes=OTP_EXPIRY_MINUTES),
        attempts=0,
        consumed_at=None,
    )
    repo.save_auth_challenge(challenge)

    # Record security event
    repo.save_security_event(
        SecurityEventRecord(
            id=f"sec_{uuid4().hex[:12]}",
            account_id=account.account_id,
            event_type="LOGIN_CHALLENGE_ISSUED",
            timestamp=now,
            request_id=request_id,
            metadata={"channel": channel, "challenge_id": challenge_id},
        )
    )

    demo_hint = otp_plain if (settings.is_demo or settings.environment in {"development", "test"}) else None
    return challenge_id, account.account_id, demo_hint or "123456"


def verify_auth_challenge(
    challenge_id: str,
    otp_code: str,
    request_id: str | None = None,
) -> tuple[str, str, SessionRecord, DigiInAccountRecord]:
    """Verify OTP challenge, handle attempt limits, and establish sovereign session."""
    challenge = repo.get_auth_challenge(challenge_id)
    now = datetime.now(UTC)

    if not challenge:
        raise ValueError("Invalid or non-existent authentication challenge")

    if challenge.consumed_at is not None:
        raise ValueError("Authentication challenge already consumed")

    if _to_utc(challenge.expires_at) < now:
        raise ValueError("Authentication challenge has expired")

    if challenge.attempts >= MAX_OTP_ATTEMPTS:
        raise ValueError("Challenge locked: maximum OTP verification attempts exceeded")

    account = repo.get_account_by_id(challenge.account_id)
    if not account or account.status != "ACTIVE":
        raise ValueError("Account is inactive or suspended")

    # Validate salted hash
    is_valid = verify_secret(otp_code, challenge.challenge_hash)
    if not is_valid:
        # Increment attempt counter
        updated_ch = AuthChallengeRecord(
            challenge_id=challenge.challenge_id,
            account_id=challenge.account_id,
            channel=challenge.channel,
            challenge_hash=challenge.challenge_hash,
            expires_at=challenge.expires_at,
            attempts=challenge.attempts + 1,
            consumed_at=None,
        )
        repo.save_auth_challenge(updated_ch)

        repo.save_security_event(
            SecurityEventRecord(
                id=f"sec_{uuid4().hex[:12]}",
                account_id=account.account_id,
                event_type="LOGIN_FAILED",
                timestamp=now,
                request_id=request_id,
                metadata={"challenge_id": challenge_id, "attempt": updated_ch.attempts},
            )
        )
        raise ValueError("Invalid OTP code. Please verify the code and try again.")

    # Mark consumed
    consumed_ch = AuthChallengeRecord(
        challenge_id=challenge.challenge_id,
        account_id=challenge.account_id,
        channel=challenge.channel,
        challenge_hash=challenge.challenge_hash,
        expires_at=challenge.expires_at,
        attempts=challenge.attempts + 1,
        consumed_at=now,
    )
    repo.save_auth_challenge(consumed_ch)

    # Establish session & rotate token family
    token_family = f"fam_{uuid4().hex[:12]}"
    raw_refresh = generate_refresh_token()
    refresh_hash = hash_secret(raw_refresh)
    session_id = f"sess_{uuid4().hex[:12]}"

    session_rec = SessionRecord(
        session_id=session_id,
        account_id=account.account_id,
        token_family=token_family,
        refresh_token_hash=refresh_hash,
        expires_at=now + timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS),
        created_at=now,
        revoked_at=None,
        last_used_at=now,
    )
    repo.save_session(session_rec)

    access_token = create_access_token(account.account_id, account.role)

    # Record login success event
    repo.save_security_event(
        SecurityEventRecord(
            id=f"sec_{uuid4().hex[:12]}",
            account_id=account.account_id,
            event_type="LOGIN_SUCCESS",
            timestamp=now,
            request_id=request_id,
            metadata={"session_id": session_id, "token_family": token_family},
        )
    )

    return access_token, raw_refresh, session_rec, account


def rotate_refresh_token(
    raw_refresh_token: str,
    request_id: str | None = None,
) -> tuple[str, str, SessionRecord]:
    """Single-use refresh token rotation with reuse detection and family revocation."""
    now = datetime.now(UTC)

    # Find matching session across database by verifying hash
    from app.db.models import SessionModel
    from app.db.session import get_db_session

    matching_session: SessionRecord | None = None

    with get_db_session() as s:
        all_sessions = s.query(SessionModel).order_by(SessionModel.created_at.desc()).limit(100).all()
        for sm in all_sessions:
            if verify_secret(raw_refresh_token, sm.refresh_token_hash):
                matching_session = SessionRecord(
                    session_id=sm.id,
                    account_id=sm.account_id,
                    token_family=sm.token_family,
                    refresh_token_hash=sm.refresh_token_hash,
                    created_at=sm.created_at,
                    expires_at=sm.expires_at,
                    revoked_at=sm.revoked_at,
                    last_used_at=sm.last_used_at,
                )
                break

    if matching_session is None:
        raise ValueError("Invalid refresh token")

    # Reuse detection check
    if matching_session.revoked_at is not None:
        # Compromise detected: revoke entire family immediately
        repo.revoke_token_family(matching_session.token_family)
        repo.save_security_event(
            SecurityEventRecord(
                id=f"sec_{uuid4().hex[:12]}",
                account_id=matching_session.account_id,
                event_type="REFRESH_TOKEN_REUSE_DETECTED",
                timestamp=now,
                request_id=request_id,
                metadata={
                    "token_family": matching_session.token_family,
                    "attempted_session_id": matching_session.session_id,
                },
            )
        )
        raise ValueError("Refresh token reuse detected. All active sessions in token family have been revoked.")

    if _to_utc(matching_session.expires_at) < now:
        repo.revoke_session(matching_session.session_id)
        raise ValueError("Session expired")

    # Invalidate previous token / session
    repo.revoke_session(matching_session.session_id)

    # Issue new token pair in the same token family
    new_raw_refresh = generate_refresh_token()
    new_refresh_hash = hash_secret(new_raw_refresh)
    new_session_id = f"sess_{uuid4().hex[:12]}"

    new_session = SessionRecord(
        session_id=new_session_id,
        account_id=matching_session.account_id,
        token_family=matching_session.token_family,
        refresh_token_hash=new_refresh_hash,
        expires_at=now + timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS),
        created_at=now,
        revoked_at=None,
        last_used_at=now,
    )
    repo.save_session(new_session)

    account = repo.get_account_by_id(matching_session.account_id)
    role = account.role if account else "CITIZEN"
    new_access_token = create_access_token(matching_session.account_id, role)

    repo.save_security_event(
        SecurityEventRecord(
            id=f"sec_{uuid4().hex[:12]}",
            account_id=matching_session.account_id,
            event_type="TOKEN_REFRESHED",
            timestamp=now,
            request_id=request_id,
            metadata={
                "old_session_id": matching_session.session_id,
                "new_session_id": new_session_id,
                "token_family": matching_session.token_family,
            },
        )
    )

    return new_access_token, new_raw_refresh, new_session


def logout_session(session_id: str, request_id: str | None = None) -> None:
    """Revoke active session and log audit event."""
    session = repo.get_session(session_id)
    if session:
        repo.revoke_session(session_id)
        repo.save_security_event(
            SecurityEventRecord(
                id=f"sec_{uuid4().hex[:12]}",
                account_id=session.account_id,
                event_type="LOGOUT",
                timestamp=datetime.now(UTC),
                request_id=request_id,
                metadata={"session_id": session_id},
            )
        )


def attach_identity_claim(
    account_id: str,
    claim_type: str,
    value_reference: str,
    verification_level: int,
    source: str,
) -> IdentityClaimRecord:
    """Attach verified identity claim to sovereign DigiIn account."""
    claim_id = f"claim_{uuid4().hex[:12]}"
    now = datetime.now(UTC)

    claim = IdentityClaimRecord(
        id=claim_id,
        account_id=account_id,
        claim_type=claim_type,
        value_reference=value_reference,
        verification_level=verification_level,
        source=source,
        verified_at=now,
    )
    return repo.save_identity_claim(claim)
