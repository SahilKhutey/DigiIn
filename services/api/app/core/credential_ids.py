from __future__ import annotations

import secrets


def generate_credential_id() -> str:
    """Generate high-entropy, opaque sovereign credential identifier (CRD-...)."""
    return "CRD-" + secrets.token_urlsafe(18).rstrip("=")
