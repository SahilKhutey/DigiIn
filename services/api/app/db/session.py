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


def _run_migrations(conn) -> None:
    columns_to_ensure = [
        ("documents", "owner_account_id", "VARCHAR(80)"),
        ("document_versions", "owner_account_id", "VARCHAR(80)"),
        ("document_versions", "object_id", "VARCHAR(80)"),
        ("document_versions", "sha256", "VARCHAR(64)"),
        ("document_versions", "content_type", "VARCHAR(80)"),
        ("document_versions", "size_bytes", "INTEGER"),
        ("document_versions", "processing_status", "VARCHAR(40)"),
    ]
    for table, col, col_type in columns_to_ensure:
        try:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
            conn.commit()
        except Exception:
            pass


def init_db() -> None:
    """Initialize all database tables and seed initial fixtures if empty."""
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        _run_migrations(conn)

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
