"""Sovereign Cryptographic Proof Authority and RFC 7517 Public JWKS Engine."""

from __future__ import annotations

import base64
import json
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa

# Sovereign signing keypairs (deterministic sovereign root for air-gapped JWKS public discovery)
SOVEREIGN_ED25519_SEED = b"digiin_sovereign_ed25519_key_32b"
ED25519_PRIVATE_KEY = ed25519.Ed25519PrivateKey.from_private_bytes(SOVEREIGN_ED25519_SEED)
ED25519_KEY_ID = "digiin-ed25519-key-2026"


RSA_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
RSA_KEY_ID = "digiin-rs256-key-2026"


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding_len = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(f"{data}{padding_len}".encode("ascii"))


def get_ed25519_jwk() -> dict[str, str]:
    pub_bytes = ED25519_PRIVATE_KEY.public_key().public_bytes_raw()
    return {
        "kty": "OKP",
        "crv": "Ed25519",
        "kid": ED25519_KEY_ID,
        "use": "sig",
        "alg": "EdDSA",
        "x": _b64url_encode(pub_bytes),
    }


def get_rsa_jwk() -> dict[str, str]:
    pub_numbers = RSA_PRIVATE_KEY.public_key().public_numbers()
    n_bytes = pub_numbers.n.to_bytes((pub_numbers.n.bit_length() + 7) // 8, byteorder="big")
    e_bytes = pub_numbers.e.to_bytes((pub_numbers.e.bit_length() + 7) // 8, byteorder="big")
    return {
        "kty": "RSA",
        "kid": RSA_KEY_ID,
        "use": "sig",
        "alg": "RS256",
        "n": _b64url_encode(n_bytes),
        "e": _b64url_encode(e_bytes),
    }


def get_public_jwks() -> dict[str, list[dict[str, str]]]:
    """Returns the RFC 7517 compliant JSON Web Key Set for offline public proof verification."""
    return {
        "keys": [
            get_ed25519_jwk(),
            get_rsa_jwk(),
        ]
    }


def sign_proof_token(
    claims: dict[str, Any], algorithm: str = "EdDSA"
) -> tuple[str, str, str]:
    """Signs a proof token using sovereign asymmetric private keys.

    Returns:
        (signed_jwt_token, key_id, algorithm)
    """
    if algorithm == "RS256":
        kid = RSA_KEY_ID
        alg = "RS256"
        header = {"alg": "RS256", "typ": "JWT", "kid": kid}
        header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        claims_b64 = _b64url_encode(
            json.dumps(claims, separators=(",", ":"), default=str).encode("utf-8")
        )
        signing_input = f"{header_b64}.{claims_b64}".encode("ascii")
        signature = RSA_PRIVATE_KEY.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
        token = f"{header_b64}.{claims_b64}.{_b64url_encode(signature)}"
        return token, kid, alg

    # Default to EdDSA (Ed25519)
    kid = ED25519_KEY_ID
    alg = "EdDSA"
    header = {"alg": "EdDSA", "typ": "JWT", "kid": kid}
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    claims_b64 = _b64url_encode(
        json.dumps(claims, separators=(",", ":"), default=str).encode("utf-8")
    )
    signing_input = f"{header_b64}.{claims_b64}".encode("ascii")
    signature = ED25519_PRIVATE_KEY.sign(signing_input)
    token = f"{header_b64}.{claims_b64}.{_b64url_encode(signature)}"
    return token, kid, alg


def verify_proof_token(token: str) -> tuple[dict[str, Any] | None, str | None, str | None]:
    """Verifies an asymmetric proof token against sovereign public verification keys.

    Returns:
        (claims_dict | None, key_id | None, algorithm | None)
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None, None, None

        header_b64, claims_b64, sig_b64 = parts
        header = json.loads(_b64url_decode(header_b64).decode("utf-8"))
        claims = json.loads(_b64url_decode(claims_b64).decode("utf-8"))
        sig_bytes = _b64url_decode(sig_b64)
        signing_input = f"{header_b64}.{claims_b64}".encode("ascii")

        kid = header.get("kid")
        alg = header.get("alg")

        if alg == "EdDSA" or kid == ED25519_KEY_ID:
            ED25519_PRIVATE_KEY.public_key().verify(sig_bytes, signing_input)
            return claims, ED25519_KEY_ID, "EdDSA"
        elif alg == "RS256" or kid == RSA_KEY_ID:
            RSA_PRIVATE_KEY.public_key().verify(
                sig_bytes, signing_input, padding.PKCS1v15(), hashes.SHA256()
            )
            return claims, RSA_KEY_ID, "RS256"

        return None, None, None
    except (InvalidSignature, ValueError, KeyError, json.JSONDecodeError):
        return None, None, None
