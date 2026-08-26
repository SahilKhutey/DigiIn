import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.entities import User, RefreshSession
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

def token_hash(value): return hashlib.sha256(value.encode()).hexdigest()

def issue_tokens(user, db):
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
        raise HTTPException(409, "Account already exists")
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return issue_tokens(user, db)

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return issue_tokens(user, db)

@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    data = decode_token(payload.refresh_token, "refresh")
    session = db.get(RefreshSession, data["sid"])
    if not session or session.revoked or session.token_hash != token_hash(payload.refresh_token):
        raise HTTPException(401, "Refresh session invalid")
    session.revoked = True
    user = db.get(User, data["sub"])
    db.commit()
    return issue_tokens(user, db)
