from __future__ import annotations

import re
import secrets

ACCOUNT_ID_PATTERN = re.compile(r"^DIN-[A-Z2-9]{4}-[A-Z2-9]{4}-[A-Z2-9]{4}$")
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_account_id() -> str:
    """Generate an opaque, non-semantic DigiIn Account ID.

    The identifier intentionally contains no phone number, Aadhaar fragment,
    date of birth, department code, or other personal attribute.
    """
    parts = ["".join(secrets.choice(ALPHABET) for _ in range(4)) for _ in range(3)]
    return "DIN-" + "-".join(parts)


def is_valid_account_id(value: str) -> bool:
    return bool(ACCOUNT_ID_PATTERN.fullmatch(value.strip().upper()))
