"""
DigiIn Privacy & Data Governance — Compliance Control Framework
Tracks statutory and regulatory compliance controls (DPDP Act, ISO 27001, GDPR) and evidence references.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ControlStatus:
    IMPLEMENTED = "IMPLEMENTED"
    PARTIAL = "PARTIAL"
    EXCEPTION = "EXCEPTION"
    NOT_STARTED = "NOT_STARTED"

@dataclass
class ComplianceControl:
    id: str
    code: str
    title: str
    requirement_source: str
    owner: str
    status: str = ControlStatus.IMPLEMENTED
    evidence_references: list[str] = field(default_factory=list)

class ComplianceRegistry:
    def __init__(self):
        self._controls: dict[str, ComplianceControl] = {}
        self._seed_default_controls()

    def _seed_default_controls(self):
        defaults = [
            ComplianceControl(
                id="ctrl_dpdp_purpose",
                code="DPDP_SEC_6_PURPOSE",
                title="Purpose Limitation & Specification",
                requirement_source="DPDP Act 2023 Sec 6(1)",
                owner="Chief Privacy Officer",
                status=ControlStatus.IMPLEMENTED,
                evidence_references=["app.core.privacy_governance.purpose_registry", "tests/test_phase23_privacy_governance.py"]
            ),
            ComplianceControl(
                id="ctrl_dpdp_consent",
                code="DPDP_SEC_6_CONSENT",
                title="Consent Specification & Instant Revocation",
                requirement_source="DPDP Act 2023 Sec 6(4)",
                owner="Security Engineering",
                status=ControlStatus.IMPLEMENTED,
                evidence_references=["app.core.privacy_governance.consent_engine"]
            ),
            ComplianceControl(
                id="ctrl_dpdp_erasure",
                code="DPDP_SEC_12_ERASURE",
                title="Right to Correction & Erasure",
                requirement_source="DPDP Act 2023 Sec 12(3)",
                owner="Data Lifecycle Operations",
                status=ControlStatus.IMPLEMENTED,
                evidence_references=["app.core.privacy_governance.retention_engine", "app.core.privacy_governance.account_closure"]
            ),
            ComplianceControl(
                id="ctrl_dpdp_portability",
                code="DPDP_SEC_11_PORTABILITY",
                title="Citizen Data Access & Portability",
                requirement_source="DPDP Act 2023 Sec 11",
                owner="Platform Engineering",
                status=ControlStatus.IMPLEMENTED,
                evidence_references=["app.core.privacy_governance.data_export"]
            ),
        ]
        for c in defaults:
            self._controls[c.code] = c

    def get_control(self, code: str) -> ComplianceControl | None:
        return self._controls.get(code)

    def get_compliance_posture(self) -> dict[str, Any]:
        total = len(self._controls)
        implemented = sum(1 for c in self._controls.values() if c.status == ControlStatus.IMPLEMENTED)
        coverage_pct = round((implemented / total) * 100.0, 1) if total > 0 else 0.0
        return {
            "totalControls": total,
            "implemented": implemented,
            "evidenceCoverage": f"{coverage_pct}%",
            "frameworks": ["DPDP Act 2023", "ISO/IEC 27701:2019", "GDPR Article 5/6"]
        }
