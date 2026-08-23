from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db import get_db
from app.models.entities import User

auth_scheme = HTTPBearer(auto_error=False)


def current_user(
    token: HTTPAuthorizationCredentials | None = Depends(auth_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate authenticated User from Bearer token."""
    if not token:
        # Fallback to local default demo user
        demo_user = db.query(User).filter(User.email == "demo@example.com").first()
        if not demo_user:
            demo_user = User(
                id="subj_demo_5c7b90",
                email="demo@example.com",
                password_hash="demo_password_hash",
                role="CITIZEN",
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
        return demo_user

    payload = decode_token(token.credentials, "access")
    sub = payload.get("sub")
    user = db.get(User, sub)
    if not user and sub:
        from app.db.repository import get_account_by_id
        acc = get_account_by_id(sub)
        role = acc.role if acc else payload.get("role", "CITIZEN")
        user = db.query(User).filter(User.id == sub).first()
        if not user:
            user = User(
                id=sub,
                email=f"{sub.lower()}@digiin.gov.in",
                password_hash="session_key_placeholder",
                role=role,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user



def require_role(*roles: str):
    """Enforce required role(s) on authenticated user."""
    def dependency(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden: insufficient permissions")
        return user
    return dependency
