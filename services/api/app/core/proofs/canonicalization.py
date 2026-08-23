"""
DigiIn Cryptographic Proof Subsystem — RFC 8785 JSON Canonicalization Scheme
Ensures stable byte serialization across all platforms, preventing signature failure from whitespace or key ordering.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonicalize_proof_payload(payload: dict[str, Any]) -> bytes:
    """
    Produce deterministic, canonical byte representation of JSON payload according to RFC 8785 rules:
    - Keys sorted lexicographically
    - No whitespace between delimiters
    - Strict UTF-8 encoding
    """
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

def compute_payload_digest(payload: dict[str, Any]) -> str:
    """Compute SHA-256 binary hash digest of the canonicalized payload."""
    canonical_bytes = canonicalize_proof_payload(payload)
    return hashlib.sha256(canonical_bytes).hexdigest()
