"""
DigiIn Cryptographic Proof Subsystem — Proof Signing Service
Asymmetric digital signature generator using Ed25519 and RFC 8785 canonical serialization.
"""

from __future__ import annotations

import base64
import secrets
import time
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .canonicalization import canonicalize_proof_payload, compute_payload_digest
from .claim_model import VerifiedClaim
from .key_management import KeyManager


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

class ProofSigningService:
    def __init__(self, key_manager: KeyManager):
        self.key_manager = key_manager

    def mint_signed_proof(
        self,
        subject_id: str,
        claims: list[VerifiedClaim],
        issuer_identifier: str = "did:digiin:authority:root",
        purpose: str | None = None,
        proof_type: str = "EDUCATION_VERIFIED",
        ttl_seconds: int = 86400 * 90  # 90 days
    ) -> dict[str, Any]:
        """Mint, canonicalize, and cryptographically sign a DigiIn verifiable proof."""
        active_key = self.key_manager.get_active_signing_key()
        if not active_key:
            raise RuntimeError("KEY_ERROR: No active signing key available for proof generation.")

        proof_id = f"prf_01K{secrets.token_hex(10).upper()}"
        now = time.time()
        expires_at = now + ttl_seconds

        # Construct unsigned payload
        payload = {
            "version": "1.0.0",
            "proofId": proof_id,
            "issuer": issuer_identifier,
            "subject": subject_id,
            "proofType": proof_type,
            "purpose": purpose or "GENERAL_VERIFICATION",
            "claims": [c.to_dict() for c in claims],
            "issuedAt": now,
            "expiresAt": expires_at,
            "keyId": active_key.key_id,
        }

        # 1. Canonicalize
        canonical_bytes = canonicalize_proof_payload(payload)
        digest = compute_payload_digest(payload)

        # 2. Sign canonical bytes with Ed25519 private key
        priv_key = Ed25519PrivateKey.from_private_bytes(active_key.private_key_bytes)
        sig_bytes = priv_key.sign(canonical_bytes)
        signature = _b64_encode(sig_bytes)

        # 3. Assemble complete signed proof object
        proof_object = {
            **payload,
            "digest": digest,
            "signature": signature,
            "status": "ACTIVE",
            "statusReference": f"https://verify.digiin.in/status/{proof_id}",
        }
        return proof_object
