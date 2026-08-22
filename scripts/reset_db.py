#!/usr/bin/env python3
"""Database Reset and Seed Utility for DigiLocker X (DigiIn).

Drops and recreates SQLite/PostgreSQL tables and seeds authoritative multi-persona fixtures.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add services/api to sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "services" / "api"))
sys.path.insert(0, str(root_dir))

from app.db.models import Base
from app.db.session import engine, init_db
from scripts.seed_demo_data import seed_multi_persona_data


def reset_and_seed_database() -> None:
    print(">>> 1. Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)

    print(">>> 2. Initializing fresh database schemas...")
    Base.metadata.create_all(bind=engine)

    print(">>> 3. Seeding multi-persona digital public infrastructure fixtures...")
    seed_multi_persona_data()

    print("\nSUCCESS: DATABASE RESET AND RE-SEEDED SUCCESSFULLY!")


if __name__ == "__main__":
    reset_and_seed_database()
