import hashlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db import get_db
from app.domain.auth_models import (
    AuthChallengeRequest,
    AuthChallengeResponse,
    AuthChallengeVerifyRequest,
    AuthChallengeVerifyResponse,
    RefreshTokenPayload,
    SessionInfoResponse,
)
from app.models.entities import RefreshSession, User
from app.services.auth_service import (
    create_auth_challenge,
    logout_session,
    rotate_refresh_token,
    verify_auth_challenge,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def token_hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def issue_tokens(user: User, db: Session) -> dict[str, str]:
    session_id = str(uuid.uuid4())
    refresh = create_refresh_token(user.id, session_id)
    db.add(RefreshSession(id=session_id, user_id=user.id, token_hash=token_hash(refresh)))
    db.commit()
    return {
        "access_token": create_access_token(user.id, user.role),
        "refresh_token": refresh,
    }


@router.post("/register")
def register(payload: dict[str, str], db: Session = Depends(get_db)):
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Missing email or password")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Account already exists")
    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return issue_tokens(user, db)


@router.post("/login")
def login(payload: dict[str, str], db: Session = Depends(get_db)):
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Missing email or password")
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return issue_tokens(user, db)


@router.post("/refresh")
def refresh(payload: dict[str, str], request: Request, db: Session = Depends(get_db)):
    refresh_token = payload.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Missing refresh token")

    req_id = request.headers.get("X-Request-ID")
    try:
        access, new_refresh, sess = rotate_refresh_token(
            raw_refresh_token=refresh_token,
            request_id=req_id,
        )
        return {
            "access_token": access,
            "refresh_token": new_refresh,
            "token_type": "Bearer",
            "expires_in": 900,
            "account_id": sess.account_id,
            "session_id": sess.session_id,
        }
    except ValueError as err:
        if "reuse detected" in str(err).lower():
            raise HTTPException(status_code=401, detail=str(err))
        # Fallback to legacy JWT decode token
        try:
            data = decode_token(refresh_token, "refresh")
            session = db.get(RefreshSession, data["sid"])
            if not session or session.revoked or session.token_hash != token_hash(refresh_token):
                raise HTTPException(status_code=401, detail="Refresh session invalid")
            session.revoked = True
            user = db.get(User, data["sub"])
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            db.commit()
            return issue_tokens(user, db)
        except Exception:
            raise HTTPException(status_code=401, detail=str(err))


# --- Phase 3 Hardened Identity & Session Endpoints ---

@router.post("/challenge", response_model=AuthChallengeResponse)
def issue_challenge(payload: AuthChallengeRequest, request: Request) -> AuthChallengeResponse:
    req_id = request.headers.get("X-Request-ID")
    ch_id, acc_id, hint = create_auth_challenge(
        phone_number=payload.phone_number,
        channel=payload.channel,
        request_id=req_id,
    )
    return AuthChallengeResponse(
        challenge_id=ch_id,
        account_id=acc_id,
        channel=payload.channel,
        expires_in_seconds=300,
        demo_otp_hint=hint,
        message="Authentication challenge dispatched. Enter the 6-digit OTP code.",
    )


@router.post("/verify", response_model=AuthChallengeVerifyResponse)
def verify_challenge(payload: AuthChallengeVerifyRequest, request: Request) -> AuthChallengeVerifyResponse:
    req_id = request.headers.get("X-Request-ID")
    try:
        access, refresh_val, sess, acc = verify_auth_challenge(
            challenge_id=payload.challenge_id,
            otp_code=payload.otp_code,
            request_id=req_id,
        )
        return AuthChallengeVerifyResponse(
            access_token=access,
            refresh_token=refresh_val,
            token_type="Bearer",
            expires_in=900,
            account_id=acc.account_id,
            role=acc.role,
            session_id=sess.session_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rotate-refresh", response_model=AuthChallengeVerifyResponse)
def rotate_refresh(payload: RefreshTokenPayload, request: Request) -> AuthChallengeVerifyResponse:
    req_id = request.headers.get("X-Request-ID")
    try:
        access, new_refresh, sess = rotate_refresh_token(
            raw_refresh_token=payload.refresh_token,
            request_id=req_id,
        )
        return AuthChallengeVerifyResponse(
            access_token=access,
            refresh_token=new_refresh,
            token_type="Bearer",
            expires_in=900,
            account_id=sess.account_id,
            role="CITIZEN",
            session_id=sess.session_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
def logout(session_id: str, request: Request) -> dict[str, str]:
    req_id = request.headers.get("X-Request-ID")
    logout_session(session_id, request_id=req_id)
    return {"status": "logged_out", "session_id": session_id}


@router.get("/session/{session_id}", response_model=SessionInfoResponse)
def get_session_info(session_id: str) -> SessionInfoResponse:
    import app.db.repository as r
    sess = r.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionInfoResponse(
        session_id=sess.session_id,
        account_id=sess.account_id,
        token_family=sess.token_family,
        is_active=(sess.revoked_at is None),
        created_at=sess.created_at,
        expires_at=sess.expires_at,
        last_used_at=sess.last_used_at,
    )
