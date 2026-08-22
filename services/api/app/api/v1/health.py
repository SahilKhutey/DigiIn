from fastapi import APIRouter

from app.db import check_db_health

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "digilocker-x-api",
        "database": check_db_health(),
    }
