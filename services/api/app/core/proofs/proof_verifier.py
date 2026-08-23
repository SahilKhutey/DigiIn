"""
DigiIn Cryptographic Proof Subsystem — Multi-Stage Proof Verifier
Executes a 6-stage verification sequence: Signature -> Issuer Trust -> Key Validity -> Active Status -> Expiration -> Purpose Policy.
"""

from __future__ import annotations

import base64
import time
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .canonicalization import canonicalize_proof_payload
from .key_management import KeyManager, KeyStatus
from .trust_registry import TrustRegistry


def _b64_decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))

class VerificationOutcome:
    def __init__(
        self,
        valid: bool,
        signature_valid: bool,
        issuer_trusted: bool,
        key_valid: bool,
        status_valid: bool,
        not_expired: bool,
        policy_satisfied: bool,
        proof_id: str,
        reason: str | None = None,
        claims: list | None = None
    ):
        self.valid = valid
        self.signature_valid = signature_valid
        self.issuer_trusted = issuer_trusted
        self.key_valid = key_valid
        self.status_valid = status_valid
        self.not_expired = not_expired
        self.policy_satisfied = policy_satisfied
        self.proof_id = proof_id
        self.reason = reason
        self.claims = claims or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "signatureValid": self.signature_valid,
            "issuerTrusted": self.issuer_trusted,
            "keyValid": self.key_valid,
            "statusValid": self.status_valid,
            "notExpired": self.not_expired,
            "policySatisfied": self.policy_satisfied,
            "proofId": self.proof_id,
            "reason": self.reason,
            "claims": self.claims,
        }

class ProofVerifier:
    def __init__(self, key_manager: KeyManager, trust_registry: TrustRegistry):
        self.key_manager = key_manager
        self.trust_registry = trust_registry

    def verify(
        self,
        proof_object: dict[str, Any],
        expected_purpose: str | None = None,
        now: float | None = None
    ) -> VerificationOutcome:
        current_time = now or time.time()
        proof_id = proof_object.get("proofId", "unknown")

        # --- Stage 1: Key & Issuer Lookup ---
        key_id = proof_object.get("keyId")
        signing_key = self.key_manager.get_key(key_id) if key_id else None
        key_valid = signing_key is not None and signing_key.status in (KeyStatus.ACTIVE, KeyStatus.ROTATING, KeyStatus.RETIRED)
        if not key_valid:
            return VerificationOutcome(
                valid=False, signature_valid=False, issuer_trusted=False, key_valid=False,
                status_valid=False, not_expired=False, policy_satisfied=False, proof_id=proof_id,
                reason="KEY_INVALID: Signing key unknown, expired, or revoked."
            )

        issuer = proof_object.get("issuer", "")
        proof_type = proof_object.get("proofType", "")
        issuer_trusted = self.trust_registry.is_issuer_trusted(issuer, proof_type)
        if not issuer_trusted:
            return VerificationOutcome(
                valid=False, signature_valid=False, issuer_trusted=False, key_valid=key_valid,
                status_valid=False, not_expired=False, policy_satisfied=False, proof_id=proof_id,
                reason=f"ISSUER_UNTRUSTED: Issuer '{issuer}' is not authorized for proof type '{proof_type}'."
            )

        # --- Stage 2: Mathematical Signature Verification ---
        signature_b64 = proof_object.get("signature", "")
        # Extract signing payload by omitting signature and dynamic status fields
        unsigned_payload = {
            "version": proof_object.get("version"),
            "proofId": proof_object.get("proofId"),
            "issuer": proof_object.get("issuer"),
            "subject": proof_object.get("subject"),
            "proofType": proof_object.get("proofType"),
            "purpose": proof_object.get("purpose"),
            "claims": proof_object.get("claims", []),
            "issuedAt": proof_object.get("issuedAt"),
            "expiresAt": proof_object.get("expiresAt"),
            "keyId": proof_object.get("keyId"),
        }

        canonical_bytes = canonicalize_proof_payload(unsigned_payload)
        signature_valid = False
        try:
            pub_key = Ed25519PublicKey.from_public_bytes(signing_key.public_bytes)
            pub_key.verify(_b64_decode(signature_b64), canonical_bytes)
            signature_valid = True
        except (InvalidSignature, ValueError, Exception):
            signature_valid = False

        if not signature_valid:
            return VerificationOutcome(
                valid=False, signature_valid=False, issuer_trusted=issuer_trusted, key_valid=key_valid,
                status_valid=False, not_expired=False, policy_satisfied=False, proof_id=proof_id,
                reason="SIGNATURE_INVALID: Cryptographic proof has been modified, corrupted, or forged."
            )

        # --- Stage 3: Status Check (Revocation / Suspension) ---
        status = proof_object.get("status", "ACTIVE")
        status_valid = status == "ACTIVE"
        if not status_valid:
            return VerificationOutcome(
                valid=False, signature_valid=True, issuer_trusted=issuer_trusted, key_valid=key_valid,
                status_valid=False, not_expired=False, policy_satisfied=False, proof_id=proof_id,
                reason=f"PROOF_{status}: Proof is no longer active (Status: {status})."
            )

        # --- Stage 4: Expiration Check ---
        expires_at = proof_object.get("expiresAt", 0)
        not_expired = current_time <= expires_at
        if not not_expired:
            return VerificationOutcome(
                valid=False, signature_valid=True, issuer_trusted=issuer_trusted, key_valid=key_valid,
                status_valid=status_valid, not_expired=False, policy_satisfied=False, proof_id=proof_id,
                reason="PROOF_EXPIRED: The validity period for this proof has elapsed."
            )

        # --- Stage 5: Purpose & Policy Restriction Check ---
        proof_purpose = proof_object.get("purpose")
        if expected_purpose and proof_purpose and proof_purpose != "GENERAL_VERIFICATION" and proof_purpose != expected_purpose:
            return VerificationOutcome(
                valid=False, signature_valid=True, issuer_trusted=issuer_trusted, key_valid=key_valid,
                status_valid=status_valid, not_expired=not_expired, policy_satisfied=False, proof_id=proof_id,
                reason=f"PURPOSE_MISMATCH: Proof issued for '{proof_purpose}' cannot be used for '{expected_purpose}'."
            )

        # --- Success ---
        return VerificationOutcome(
            valid=True,
            signature_valid=True,
            issuer_trusted=True,
            key_valid=True,
            status_valid=True,
            not_expired=True,
            policy_satisfied=True,
            proof_id=proof_id,
            reason=None,
            claims=proof_object.get("claims", [])
        )
