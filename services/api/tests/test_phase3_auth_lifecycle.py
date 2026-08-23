from uuid import uuid4

import pytest

from app.core.ids import is_valid_account_id
from app.db.repository import (
    get_identity_claims,
    get_session,
    list_security_events,
)
from app.services.auth_service import (
    attach_identity_claim,
    create_auth_challenge,
    logout_session,
    rotate_refresh_token,
    verify_auth_challenge,
)


def test_phase3_auth_full_lifecycle_and_rotation():
    phone = f"+91 98{uuid4().int % 100000000:08d}"

    # 1. Issue Challenge
    ch_id, account_id, hint = create_auth_challenge(phone, channel="SMS")
    assert ch_id.startswith("ch_")
    assert is_valid_account_id(account_id)
    assert hint == "123456"

    # 2. Verify Challenge & Establish Session
    access_1, refresh_1, sess_1, acc = verify_auth_challenge(ch_id, "123456")
    assert acc.account_id == account_id
    assert sess_1.account_id == account_id
    assert sess_1.revoked_at is None
    assert len(access_1) > 20
    assert len(refresh_1) > 20

    # 3. Rotate Refresh Token (Token A -> Token B, Token A invalidated)
    access_2, refresh_2, sess_2 = rotate_refresh_token(refresh_1)
    assert sess_2.token_family == sess_1.token_family
    assert sess_2.session_id != sess_1.session_id

    # Verify old session is revoked
    old_sess = get_session(sess_1.session_id)
    assert old_sess is not None
    assert old_sess.revoked_at is not None

    # Verify new session is active
    current_sess = get_session(sess_2.session_id)
    assert current_sess is not None
    assert current_sess.revoked_at is None

    # 4. Logout / Session Revocation
    logout_session(sess_2.session_id)
    logged_out_sess = get_session(sess_2.session_id)
    assert logged_out_sess is not None
    assert logged_out_sess.revoked_at is not None

    # 5. Verify Security Audit Events
    events = list_security_events(account_id=account_id)
    event_types = [e.event_type for e in events]
    assert "LOGIN_CHALLENGE_ISSUED" in event_types
    assert "LOGIN_SUCCESS" in event_types
    assert "TOKEN_REFRESHED" in event_types
    assert "LOGOUT" in event_types


def test_phase3_otp_attempt_limits_lock_challenge():
    phone = f"+91 97{uuid4().int % 100000000:08d}"
    ch_id, account_id, _ = create_auth_challenge(phone)

    # Attempt 1: wrong OTP
    with pytest.raises(ValueError, match="Invalid OTP code"):
        verify_auth_challenge(ch_id, "000001")

    # Attempt 2: wrong OTP
    with pytest.raises(ValueError, match="Invalid OTP code"):
        verify_auth_challenge(ch_id, "000002")

    # Attempt 3: wrong OTP
    with pytest.raises(ValueError, match="Invalid OTP code"):
        verify_auth_challenge(ch_id, "000003")

    # Attempt 4: challenge locked
    with pytest.raises(ValueError, match="Challenge locked: maximum OTP verification attempts exceeded"):
        verify_auth_challenge(ch_id, "123456")


def test_phase3_refresh_token_reuse_detection_revokes_family():
    phone = f"+91 96{uuid4().int % 100000000:08d}"
    ch_id, account_id, _ = create_auth_challenge(phone)

    # Establish initial session
    _, refresh_1, sess_1, _ = verify_auth_challenge(ch_id, "123456")
    family_id = sess_1.token_family

    # Legitimate rotation (Token 1 -> Token 2)
    _, refresh_2, sess_2 = rotate_refresh_token(refresh_1)
    assert sess_2.token_family == family_id

    # Malicious actor attempts to REUSE already-rotated Token 1!
    with pytest.raises(ValueError, match="Refresh token reuse detected"):
        rotate_refresh_token(refresh_1)

    # Entire family should now be revoked, including Token 2!
    current_sess_2 = get_session(sess_2.session_id)
    assert current_sess_2 is not None
    assert current_sess_2.revoked_at is not None

    # Now attempting to use Token 2 also fails
    with pytest.raises(ValueError, match="Refresh token reuse detected"):
        rotate_refresh_token(refresh_2)


def test_phase3_account_separate_from_identity_claims():
    phone = f"+91 95{uuid4().int % 100000000:08d}"
    ch_id, account_id, _ = create_auth_challenge(phone)
    _, _, _, acc = verify_auth_challenge(ch_id, "123456")

    # Account exists independently without government identity verification
    assert is_valid_account_id(acc.account_id)
    claims_before = get_identity_claims(acc.account_id)
    assert len(claims_before) == 0

    # Attach verified identity claim (e.g. Aadhaar eKYC, Class XII certificate)
    claim = attach_identity_claim(
        account_id=acc.account_id,
        claim_type="AADHAAR_DEMOGRAPHICS",
        value_reference="uidai_ref_sha256_hash",
        verification_level=4,
        source="UIDAI Central Identity Repository",
    )
    assert claim.verification_level == 4
    assert claim.source == "UIDAI Central Identity Repository"

    claims_after = get_identity_claims(acc.account_id)
    assert len(claims_after) == 1
    assert claims_after[0].claim_type == "AADHAAR_DEMOGRAPHICS"
