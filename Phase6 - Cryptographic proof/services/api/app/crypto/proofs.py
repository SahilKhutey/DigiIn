from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption,
)


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def canonical_json(value: dict[str, Any]) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class Proof:
    proof_id: str
    issuer: str
    audience: str
    issued_at: int
    expires_at: int
    nonce: str
    claims: dict[str, Any]
    key_id: str
    signature: str

    def signing_payload(self) -> dict[str, Any]:
        return {
            "proof_id": self.proof_id,
            "issuer": self.issuer,
            "audience": self.audience,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "nonce": self.nonce,
            "claims": self.claims,
            "key_id": self.key_id,
        }


def generate_keypair() -> tuple[bytes, bytes]:
    private = Ed25519PrivateKey.generate()
    private_bytes = private.private_bytes(
        Encoding.Raw,
        PrivateFormat.Raw,
        NoEncryption(),
    )
    public_bytes = private.public_key().public_bytes(
        Encoding.Raw,
        PublicFormat.Raw,
    )
    return private_bytes, public_bytes


def sign_proof(
    *,
    proof_id: str,
    issuer: str,
    audience: str,
    nonce: str,
    claims: dict[str, Any],
    key_id: str,
    private_key: bytes,
    expires_at: int,
    issued_at: int | None = None,
) -> Proof:
    issued = issued_at or int(datetime.now(timezone.utc).timestamp())
    unsigned = {
        "proof_id": proof_id,
        "issuer": issuer,
        "audience": audience,
        "issued_at": issued,
        "expires_at": expires_at,
        "nonce": nonce,
        "claims": claims,
        "key_id": key_id,
    }
    signature = Ed25519PrivateKey.from_private_bytes(private_key).sign(
        canonical_json(unsigned)
    )
    return Proof(
        **unsigned,
        signature=_b64(signature),
    )


def verify_proof(
    proof: Proof,
    *,
    public_key: bytes,
    expected_issuer: str,
    expected_audience: str,
    expected_nonce: str,
    now: int | None = None,
) -> bool:
    current = now or int(datetime.now(timezone.utc).timestamp())

    if proof.issuer != expected_issuer:
        return False
    if proof.audience != expected_audience:
        return False
    if proof.nonce != expected_nonce:
        return False
    if proof.expires_at <= current:
        return False
    if proof.issued_at > current + 60:
        return False

    try:
        Ed25519PublicKey.from_public_bytes(public_key).verify(
            _unb64(proof.signature),
            canonical_json(proof.signing_payload()),
        )
        return True
    except (InvalidSignature, ValueError):
        return False
