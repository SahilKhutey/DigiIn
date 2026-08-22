"""SQLAlchemy database engine and session configuration."""

from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv("DIGIIN_DATABASE_URL", "sqlite:///./digiin_database.db")

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions with automatic commit and rollback."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Initialize all database tables and seed initial fixtures if empty."""
    Base.metadata.create_all(bind=engine)
    from app.db.repository import seed_default_data_if_empty

    seed_default_data_if_empty()


def check_db_health() -> dict[str, str]:
    """Checks database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        dialect = engine.dialect.name
        return {"status": "connected", "dialect": dialect}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
