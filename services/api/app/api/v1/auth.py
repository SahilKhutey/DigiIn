import hashlib
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db import get_db
from app.models.entities import RefreshSession, User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def token_hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def issue_tokens(user: User, db: Session) -> TokenResponse:
    session_id = str(uuid.uuid4())
    refresh = create_refresh_token(user.id, session_id)
    db.add(RefreshSession(id=session_id, user_id=user.id, token_hash=token_hash(refresh)))
    db.commit()
    return TokenResponse(
        access_token=create_access_token(user.id, user.role),
        refresh_token=refresh,
    )


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Account already exists")
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return issue_tokens(user, db)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return issue_tokens(user, db)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    data = decode_token(payload.refresh_token, "refresh")
    session = db.get(RefreshSession, data["sid"])
    if not session or session.revoked or session.token_hash != token_hash(payload.refresh_token):
        raise HTTPException(status_code=401, detail="Refresh session invalid")
    session.revoked = True
    user = db.get(User, data["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    db.commit()
    return issue_tokens(user, db)
