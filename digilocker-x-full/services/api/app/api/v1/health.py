from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db import get_db

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    return {"status": "ok", "service": "digilocker-x-api"}

@router.get("/ready")
def ready(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok"}
