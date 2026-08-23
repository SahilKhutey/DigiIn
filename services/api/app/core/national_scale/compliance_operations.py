"""
DigiIn National Scale — Multi-Jurisdiction Compliance Operations
Maps organizational and trust controls to statutory regulations with auditable evidence preservation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class ComplianceControl:
    control_id: str
    framework: str  # "DPDP_ACT_INDIA" | "IT_ACT_2000" | "ISO_27001" | "SOC2_TYPE_II"
    name: str
    description: str
    status: str = "COMPLIANT"
    evidence_ref: str = ""
    last_reviewed: float = field(default_factory=time.time)

class ComplianceOperationsManager:
    def __init__(self):
        self._controls: dict[str, ComplianceControl] = {}
        self._seed_default_controls()

    def _seed_default_controls(self):
        c1 = ComplianceControl(
            control_id="DPDP-SEC-01",
            framework="DPDP_ACT_INDIA",
            name="Purpose-Bound Consent Enforcement",
            description="All protected claim presentations require explicit, time-bounded citizen consent.",
            status="COMPLIANT",
            evidence_ref="ev_audit_consent_engine_v2"
        )
        c2 = ComplianceControl(
            control_id="ITACT-SEC-43A",
            framework="IT_ACT_2000",
            name="Reasonable Security Practices (AES-GCM / Ed25519)",
            description="All data at rest encrypted under KMS envelope encryption; proofs signed via Ed25519.",
            status="COMPLIANT",
            evidence_ref="ev_crypto_proof_engine_v1"
        )
        self._controls[c1.control_id] = c1
        self._controls[c2.control_id] = c2

    def list_controls(self, framework: str | None = None) -> list[ComplianceControl]:
        res = list(self._controls.values())
        if framework:
            res = [c for c in res if c.framework.upper() == framework.upper()]
        return res
