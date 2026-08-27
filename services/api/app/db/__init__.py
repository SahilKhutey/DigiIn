"""Database package initialization."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import Base, SessionLocal, check_db_health, engine, init_db


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


try:
    init_db()
except Exception:
    pass

__all__ = ["Base", "SessionLocal", "check_db_health", "engine", "get_db", "init_db"]

