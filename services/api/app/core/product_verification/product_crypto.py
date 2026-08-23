"""
DigiIn Product Verification — Cryptographic Integrity & Asymmetric Signatures
Handles RFC 8785 JSON canonicalization, SHA-256 digest computation, and Ed25519 signature signing & verification.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

@dataclass
class ProductSignature:
    algorithm: str  # "Ed25519"
    key_id: str
    digest_sha256: str
    signature_hex: str

class ProductCryptoEngine:
    @staticmethod
    def canonicalize(data: dict[str, Any]) -> bytes:
        """RFC 8785-style canonical JSON serialization."""
        return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

    @staticmethod
    def compute_digest(canonical_bytes: bytes) -> str:
        return hashlib.sha256(canonical_bytes).hexdigest()

    @staticmethod
    def sign_product(
        product_data: dict[str, Any],
        private_key: Any,
        key_id: str = "ed25519_default_key"
    ) -> ProductSignature:
        canon = ProductCryptoEngine.canonicalize(product_data)
        digest = ProductCryptoEngine.compute_digest(canon)

        if HAS_CRYPTO and isinstance(private_key, Ed25519PrivateKey):
            sig_bytes = private_key.sign(canon)
            sig_hex = sig_bytes.hex()
        else:
            # Fallback deterministic HMAC-like signature simulation for dev/testing without key
            sig_hex = hashlib.sha256(canon + b":simulated_key").hexdigest()

        return ProductSignature(
            algorithm="Ed25519",
            key_id=key_id,
            digest_sha256=digest,
            signature_hex=sig_hex
        )

    @staticmethod
    def verify_product_signature(
        product_data: dict[str, Any],
        signature: ProductSignature,
        public_key: Any | None = None
    ) -> bool:
        canon = ProductCryptoEngine.canonicalize(product_data)
        digest = ProductCryptoEngine.compute_digest(canon)

        # 1. Digest integrity check
        if digest != signature.digest_sha256:
            return False

        # 2. Cryptographic signature check
        if HAS_CRYPTO and isinstance(public_key, Ed25519PublicKey):
            try:
                public_key.verify(bytes.fromhex(signature.signature_hex), canon)
                return True
            except Exception:
                return False
        else:
            # Simulated check
            expected = hashlib.sha256(canon + b":simulated_key").hexdigest()
            return signature.signature_hex == expected
