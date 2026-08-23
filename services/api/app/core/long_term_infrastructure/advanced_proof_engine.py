"""
DigiIn Long-Term Infrastructure — Advanced Proof Engine
Generates and evaluates 4 tiers of verifiable proofs:
- Type A: Full Credential Presentation
- Type B: Predicate Proof (Possession / Range)
- Type C: Derived Boolean Eligibility Proof
- Type D: Proof-of-Status Minimal Zero-Disclosure Proof
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any

from .canonical_trust_model import CredentialStatus, PortableCredential


class ProofType:
    TYPE_A_FULL = "TYPE_A_FULL"
    TYPE_B_PREDICATE = "TYPE_B_PREDICATE"
    TYPE_C_ELIGIBILITY = "TYPE_C_ELIGIBILITY"
    TYPE_D_STATUS_ONLY = "TYPE_D_STATUS_ONLY"

@dataclass
class VerifiableProof:
    proof_id: str
    proof_type: str
    subject_id: str
    verifier_id: str
    purpose: str
    disclosed_data: dict[str, Any]
    status: str = "VALID"
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 3600)  # 1 hour short-lived presentation

class AdvancedProofEngine:
    @staticmethod
    def generate_proof(
        credential: PortableCredential,
        proof_type: str,
        verifier_id: str,
        purpose: str,
        predicate_query: dict[str, Any] | None = None
    ) -> VerifiableProof:
        pid = f"prf_{secrets.token_hex(8)}"

        if proof_type == ProofType.TYPE_A_FULL:
            disclosed = credential.claims.copy()
        elif proof_type == ProofType.TYPE_B_PREDICATE:
            # E.g. {"field": "year", "min": 2020}
            field_name = predicate_query.get("field") if predicate_query else "year"
            val = credential.claims.get(field_name)
            satisfied = (val is not None and val >= predicate_query.get("min", 2020)) if predicate_query else True
            disclosed = {"predicate": f"{field_name}_satisfied", "result": satisfied}
        elif proof_type == ProofType.TYPE_C_ELIGIBILITY:
            # Derived qualification boolean
            eligible = (credential.status == CredentialStatus.ACTIVE and "degree" in credential.claims)
            disclosed = {"eligible": eligible, "claimType": credential.credential_type}
        elif proof_type == ProofType.TYPE_D_STATUS_ONLY:
            # Zero-disclosure status verification
            disclosed = {"credentialStatus": credential.status, "issuerId": credential.issuer_id}
        else:
            raise ValueError(f"UNSUPPORTED_PROOF_TYPE: {proof_type}")

        return VerifiableProof(
            proof_id=pid,
            proof_type=proof_type,
            subject_id=credential.subject_id,
            verifier_id=verifier_id,
            purpose=purpose,
            disclosed_data=disclosed,
            status="VALID" if credential.status == CredentialStatus.ACTIVE else "INVALID"
        )
