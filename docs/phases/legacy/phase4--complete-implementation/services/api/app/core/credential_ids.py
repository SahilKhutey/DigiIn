from __future__ import annotations

import secrets


def generate_credential_id() -> str:
    return "CRD-" + secrets.token_urlsafe(18).rstrip("=")
