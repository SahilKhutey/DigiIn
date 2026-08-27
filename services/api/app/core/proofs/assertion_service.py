"""
DigiIn Phase 4 — Signed Verification Assertion Service & Security Event Engine.

Implements:
1. Ed25519 (RFC 8032) / RFC 7515 Asymmetric Proof Signatures.
2. Audience, Purpose, and Scope Cryptographic Binding.
3. Replay Protection via Nonces & Expiration Windows (10-min TTL).
4. Machine-readable Failure Classifications.
5. Dedicated Security Event Logging.
"""

from __future__ import annotations

import base64
import hashlib
import secrets
import time
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from app.core.proofs.canonicalization import canonicalize_proof_payload


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64_decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


class CryptographicAssertionService:
    """Manages generation, signing, and cryptographic verification of DigiIn Verification Assertions."""

    def __init__(self):
        # Default Ed25519 Keypair for Root Authority
        self._private_key = Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()
        self._key_id = "digiin-ed25519-root-2026-01"
        self._key_status = "ACTIVE"  # "ACTIVE", "ROTATING", "RETIRED", "REVOKED"

        # Replay cache: set of seen assertion_ids / nonces
        self._seen_nonces: set[str] = set()

        # Security events log
        self._security_events: list[dict[str, Any]] = []

    def get_public_key_bytes(self) -> bytes:
        return self._public_key.public_bytes_raw()

    def get_public_key_b64(self) -> str:
        return _b64_encode(self.get_public_key_bytes())

    def rotate_key(self) -> str:
        """Rotate to a new root signing keypair."""
        self._private_key = Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()
        self._key_id = f"digiin-ed25519-root-{int(time.time())}"
        self._key_status = "ACTIVE"
        return self._key_id

    def revoke_key(self):
        """Emergency revoke current signing key."""
        self._key_status = "REVOKED"

    def mint_signed_assertion(
        self,
        subject: str,  # DigiIn Account ID (e.g. DI-7K4M-9Q2X-8P6R)
        audience: str,  # Requesting service ID (e.g. dept_du_scholarship_portal)
        purpose: str,  # Declared purpose (e.g. scholarship_eligibility)
        scope: list[str],  # List of approved attribute scopes
        claims: dict[str, Any],  # Verified claim assertions
        ttl_seconds: int = 600,  # 10 minutes default
        request_id: str | None = None,
    ) -> dict[str, Any]:
        """Generates, canonicalizes, and cryptographically signs a Verification Assertion."""
        if self._key_status == "REVOKED":
            raise RuntimeError("KEY_REVOKED: Current signing key is revoked. Cannot sign assertions.")

        now_ts = time.time()
        assertion_id = f"VA-{uuid4().hex[:10].upper()}"
        nonce = secrets.token_hex(12)

        payload: dict[str, Any] = {
            "version": "1.0.0",
            "assertion_id": assertion_id,
            "request_id": request_id or f"VR-{uuid4().hex[:6].upper()}",
            "issuer": "DigiIn Trust Network",
            "subject": subject,
            "audience": audience,
            "purpose": purpose,
            "scope": sorted(scope),
            "claims": claims,
            "raw_files_transferred_bytes": 0,  # Minimum disclosure guarantee
            "issued_at": int(now_ts),
            "expires_at": int(now_ts + ttl_seconds),
            "nonce": nonce,
            "key_id": self._key_id,
        }

        # Canonicalize payload according to RFC 8785
        canonical_bytes = canonicalize_proof_payload(payload)
        digest = hashlib.sha256(canonical_bytes).hexdigest()

        # Sign with Ed25519 private key
        sig_bytes = self._private_key.sign(canonical_bytes)
        signature = _b64_encode(sig_bytes)

        signed_assertion = {
            **payload,
            "digest_sha256": digest,
            "signature": signature,
            "algorithm": "Ed25519 (RFC 8032) / JWS (RFC 7515)",
        }
        return signed_assertion

    def verify_signed_assertion(
        self,
        assertion: dict[str, Any],
        expected_audience: str | None = None,
        expected_purpose: str | None = None,
        enforce_replay_protection: bool = True,
    ) -> dict[str, Any]:
        """Cryptographically verifies assertion signature, validity window, audience, and purpose."""
        assertion_id = assertion.get("assertion_id", "UNKNOWN")
        nonce = assertion.get("nonce", "")

        # 1. Key Status Check
        if self._key_status == "REVOKED":
            self._log_security_event("KEY_REVOKED", assertion, "Signing key is in revoked state.")
            return {"valid": False, "error_code": "KEY_REVOKED", "message": "Signing key has been revoked."}

        # 2. Expiry Check
        now_ts = time.time()
        expires_at = assertion.get("expires_at", 0)
        if now_ts > expires_at:
            self._log_security_event("EXPIRED", assertion, f"Assertion expired at {expires_at} (now {int(now_ts)}).")
            return {"valid": False, "error_code": "EXPIRED", "message": "Verification assertion has expired."}

        # 3. Audience Binding Check
        if expected_audience and assertion.get("audience") != expected_audience:
            self._log_security_event(
                "WRONG_AUDIENCE",
                assertion,
                f"Expected audience '{expected_audience}', but assertion audience is '{assertion.get('audience')}'.",
            )
            return {
                "valid": False,
                "error_code": "WRONG_AUDIENCE",
                "message": f"Assertion was not issued for requesting service '{expected_audience}'.",
            }

        # 4. Purpose Binding Check
        if expected_purpose and assertion.get("purpose") != expected_purpose:
            self._log_security_event(
                "WRONG_PURPOSE",
                assertion,
                f"Expected purpose '{expected_purpose}', but assertion purpose is '{assertion.get('purpose')}'.",
            )
            return {
                "valid": False,
                "error_code": "WRONG_PURPOSE",
                "message": "Assertion purpose does not match declared transaction purpose.",
            }

        # 5. Replay Protection Check
        if enforce_replay_protection and nonce:
            if nonce in self._seen_nonces:
                self._log_security_event("REPLAY_DETECTED", assertion, f"Replay attempt detected for nonce: {nonce}")
                return {
                    "valid": False,
                    "error_code": "REPLAY_DETECTED",
                    "message": "Assertion replay detected. Each assertion may only be presented once.",
                }
            self._seen_nonces.add(nonce)

        # 6. Mathematical Signature Verification
        signature_b64 = assertion.get("signature")
        if not signature_b64:
            self._log_security_event("MALFORMED", assertion, "Missing signature in assertion payload.")
            return {"valid": False, "error_code": "MALFORMED", "message": "Assertion is missing digital signature."}

        unsigned_payload = {k: v for k, v in assertion.items() if k not in ("signature", "digest_sha256", "algorithm")}
        try:
            canonical_bytes = canonicalize_proof_payload(unsigned_payload)
            sig_bytes = _b64_decode(signature_b64)
            self._public_key.verify(sig_bytes, canonical_bytes)
        except (InvalidSignature, ValueError) as exc:
            self._log_security_event("INVALID_SIGNATURE", assertion, f"Signature check failed: {str(exc)}")
            return {
                "valid": False,
                "error_code": "INVALID_SIGNATURE",
                "message": "Cryptographic signature is invalid or payload has been tampered with.",
            }

        return {
            "valid": True,
            "assertion_id": assertion_id,
            "issuer": assertion.get("issuer"),
            "subject": assertion.get("subject"),
            "audience": assertion.get("audience"),
            "purpose": assertion.get("purpose"),
            "scope": assertion.get("scope"),
            "claims": assertion.get("claims"),
            "raw_files_transferred_bytes": 0,
            "verified_at": datetime.fromtimestamp(assertion.get("issued_at", now_ts), tz=UTC).isoformat(),
            "expires_at": datetime.fromtimestamp(expires_at, tz=UTC).isoformat(),
        }

    def _log_security_event(self, event_type: str, assertion: dict[str, Any], details: str):
        self._security_events.append(
            {
                "event_id": f"SEC-{uuid4().hex[:10].upper()}",
                "event_type": event_type,
                "actor": assertion.get("audience", "UNKNOWN"),
                "account_id": assertion.get("subject", "UNKNOWN"),
                "assertion_id": assertion.get("assertion_id", "UNKNOWN"),
                "details": details,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

    def get_security_events(self) -> list[dict[str, Any]]:
        return list(self._security_events)


# Global Singleton instance
assertion_service = CryptographicAssertionService()
