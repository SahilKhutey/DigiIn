"""
DigiIn Cryptographic Proof Subsystem (Phase 18)
Provides verified claims, canonicalization, key rotation, Ed25519 signing, trust registry, multi-stage verifier, and QR sharing.
"""

from .canonicalization import canonicalize_proof_payload, compute_payload_digest
from .claim_model import ClaimMinimizer, VerifiedClaim
from .key_management import KeyManager, KeyStatus, SigningKey
from .proof_sharing import ProofShareService
from .proof_verifier import ProofVerifier, VerificationOutcome
from .signing_service import ProofSigningService
from .trust_registry import TrustedIssuer, TrustRegistry

__all__ = [
    "VerifiedClaim",
    "ClaimMinimizer",
    "canonicalize_proof_payload",
    "compute_payload_digest",
    "KeyManager",
    "SigningKey",
    "KeyStatus",
    "TrustRegistry",
    "TrustedIssuer",
    "ProofSigningService",
    "ProofVerifier",
    "VerificationOutcome",
    "ProofShareService",
]
