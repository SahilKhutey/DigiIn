"""SQLAlchemy database engine and session configuration."""

from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

raw_db_url = (
    os.getenv("DIGIIN_DATABASE_URL")
    or os.getenv("DATABASE_URL")
    or os.getenv("SUPABASE_DB_URL")
    or "sqlite:///./digiin_database.db"
)
if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

DATABASE_URL = raw_db_url

is_sqlite = "sqlite" in DATABASE_URL
connect_args = {"check_same_thread": False} if is_sqlite else {}
engine_kwargs = {
    "connect_args": connect_args,
    "echo": False,
    "future": True,
}
if not is_sqlite:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300

engine = create_engine(DATABASE_URL, **engine_kwargs)

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
        ("document_jobs", "max_attempts", "INTEGER DEFAULT 3"),
        ("document_jobs", "available_at", "TIMESTAMP"),
        ("document_jobs", "worker_id", "VARCHAR(80)"),
        ("document_jobs", "result_json", "TEXT"),
    ]
    for table, col, col_type in columns_to_ensure:
        try:
            if conn.dialect.name == "sqlite":
                res = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
                existing_cols = {row[1] for row in res}
                if existing_cols and col not in existing_cols:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                    conn.commit()
            else:
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
