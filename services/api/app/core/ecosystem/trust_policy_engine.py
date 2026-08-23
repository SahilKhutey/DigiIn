"""
DigiIn Trust Network Expansion — Multi-Factor Trust Policy Engine
Evaluates multi-dimensional trust policies before authorizing claim exchange (Subject, Verifier, Claim, Purpose, Assurance, Consent, Trust).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .accreditation_engine import AccreditationEngine


@dataclass
class TrustPolicyDecision:
    decision: str  # "ALLOW" | "DENY"
    reason_code: str
    policy_version: str = "2026.08"
    obligations: list[str] = field(default_factory=list)
    evaluated_at: float = field(default_factory=time.time)

class TrustPolicyEngine:
    def __init__(self, accreditation_engine: AccreditationEngine):
        self.accreditation_engine = accreditation_engine

    def evaluate_policy(
        self,
        subject_id: str,
        verifier_org_id: str,
        issuer_org_id: str,
        claim_type: str,
        purpose: str,
        consent_granted: bool = True,
        claim_status: str = "ACTIVE",
        min_required_assurance: str = "A3_HIGH_ASSURANCE"
    ) -> TrustPolicyDecision:
        # 1. Active Consent Check
        if not consent_granted:
            return TrustPolicyDecision(decision="DENY", reason_code="CONSENT_REQUIRED_OR_DENIED")

        # 2. Claim Status Check
        if claim_status != "ACTIVE":
            return TrustPolicyDecision(decision="DENY", reason_code=f"CLAIM_STATUS_INVALID_{claim_status}")

        # 3. Issuer Accreditation Check
        if not self.accreditation_engine.is_issuer_accredited_for_claim(issuer_org_id, claim_type):
            return TrustPolicyDecision(decision="DENY", reason_code="ISSUER_NOT_ACCREDITED_FOR_CLAIM")

        # 4. Verifier Accreditation & Purpose Check
        ok_ver, err_ver = self.accreditation_engine.is_verifier_accredited(verifier_org_id, claim_type, purpose)
        if not ok_ver:
            return TrustPolicyDecision(decision="DENY", reason_code=err_ver or "VERIFIER_POLICY_REJECTED")

        # Policy passed
        return TrustPolicyDecision(
            decision="ALLOW",
            reason_code="AUTHORIZED_POLICY_COMPLIANT",
            obligations=["ENFORCE_AUDIENCE_RESTRICTION", "AUDIT_VERIFICATION_TRANSACTION"]
        )
