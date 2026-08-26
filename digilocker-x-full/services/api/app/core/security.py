from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_access_token(subject: str, role: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode(
        {"sub": subject, "role": role, "type": "access", "exp": expires},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

def create_refresh_token(subject: str, session_id: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days)
    return jwt.encode(
        {"sub": subject, "sid": session_id, "type": "refresh", "exp": expires},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

def decode_token(token: str, expected_type: str = "access") -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != expected_type:
            raise ValueError("wrong token type")
        if not payload.get("sub"):
            raise ValueError("missing subject")
        return payload
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
