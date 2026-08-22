#!/usr/bin/env python3
"""OpenAPI Specification Generator for DigiLocker X (DigiIn) Monorepo.

Extracts authoritative OpenAPI 3.1 JSON schema definitions directly
from the FastAPI application and writes them to docs/ and packages/schemas/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add services/api to sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "services" / "api"))
sys.path.insert(0, str(root_dir))

from app.main import app


def generate_openapi_specs() -> dict:
    openapi_schema = app.openapi()

    # Target destinations
    targets = [
        root_dir / "docs" / "openapi.json",
        root_dir / "packages" / "schemas" / "openapi.json",
    ]

    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(openapi_schema, f, indent=2)
        print(f"[OK] Generated OpenAPI schema: {target}")

    return openapi_schema


if __name__ == "__main__":
    generate_openapi_specs()
    print("SUCCESS: OpenAPI specifications generated across monorepo packages!")
