from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.api.deps import require_role
from app.models.entities import VerificationRequest

router = APIRouter(prefix="/government", tags=["government"])

@router.get("/review-queue")
def review_queue(user=Depends(require_role("OFFICER", "ADMIN")), db: Session=Depends(get_db)):
    return db.query(VerificationRequest).filter(
        VerificationRequest.status.in_([ "PENDING_REVIEW", "PENDING_CONSENT" ])
    ).order_by(VerificationRequest.created_at.asc()).all()
