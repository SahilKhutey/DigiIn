"""
DigiIn Controlled Pilot & Production Validation — Pilot Risk Register
Tracks operational risks across Security, Privacy, Reliability, Provider, and UX dimensions with mitigation status.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field


class RiskSeverity:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RiskStatus:
    OPEN = "OPEN"
    MITIGATED = "MITIGATED"
    ACCEPTED = "ACCEPTED"
    CLOSED = "CLOSED"

@dataclass
class PilotRisk:
    id: str
    title: str
    category: str  # "SECURITY" | "PRIVACY" | "RELIABILITY" | "PROVIDER" | "UX" | "OPERATIONS"
    severity: str = RiskSeverity.MEDIUM
    mitigation_plan: str = ""
    owner_id: str = ""
    status: str = RiskStatus.OPEN
    created_at: float = field(default_factory=time.time)

class PilotRiskRegister:
    def __init__(self):
        self._risks: dict[str, PilotRisk] = {}
        self._seed_default_risks()

    def _seed_default_risks(self):
        r1 = PilotRisk(
            id="risk_01",
            title="Provider CBSE Latency Burst During Admission Deadlines",
            category="PROVIDER",
            severity=RiskSeverity.HIGH,
            mitigation_plan="Enabled circuit breaker with exponential backoff & client queue buffer",
            owner_id="INTEGRATION_LEAD",
            status=RiskStatus.MITIGATED
        )
        r2 = PilotRisk(
            id="risk_02",
            title="Citizen Mobile OCR Document Quality Degradation",
            category="UX",
            severity=RiskSeverity.MEDIUM,
            mitigation_plan="Introduced real-time client-side glare/blur feedback before upload",
            owner_id="PRODUCT_LEAD",
            status=RiskStatus.MITIGATED
        )
        self._risks[r1.id] = r1
        self._risks[r2.id] = r2

    def add_risk(self, title: str, category: str, severity: str, mitigation: str, owner: str) -> PilotRisk:
        rid = f"rsk_{secrets.token_hex(8)}"
        risk = PilotRisk(
            id=rid,
            title=title,
            category=category,
            severity=severity,
            mitigation_plan=mitigation,
            owner_id=owner,
            status=RiskStatus.OPEN
        )
        self._risks[rid] = risk
        return risk

    def update_risk_status(self, risk_id: str, status: str) -> bool:
        r = self._risks.get(risk_id)
        if not r:
            return False
        r.status = status
        return True

    def get_critical_unmitigated_risks(self) -> list[PilotRisk]:
        return [r for r in self._risks.values() if r.severity == RiskSeverity.CRITICAL and r.status == RiskStatus.OPEN]
