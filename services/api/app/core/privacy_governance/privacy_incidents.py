"""
DigiIn Privacy & Data Governance — Privacy Incident & Breach Containment Workflow
Manages data breach triage, emergency containment actions (credential/token revocation, app isolation), and remediation timelines.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field


class PrivacyIncidentStage:
    DETECTED = "DETECTED"
    TRIAGED = "TRIAGED"
    CONTAINED = "CONTAINED"
    ASSESSED = "ASSESSED"
    REMEDIATED = "REMEDIATED"
    CLOSED = "CLOSED"

@dataclass
class PrivacyIncident:
    id: str
    title: str
    severity: str  # "HIGH" | "MEDIUM" | "LOW"
    stage: str = PrivacyIncidentStage.DETECTED
    affected_subjects_count: int = 0
    created_at: float = field(default_factory=time.time)
    contained_at: float | None = None
    closed_at: float | None = None
    containment_actions: list[str] = field(default_factory=list)

class PrivacyIncidentManager:
    def __init__(self):
        self._incidents: dict[str, PrivacyIncident] = {}

    def report_incident(self, title: str, severity: str, affected_count: int = 0) -> PrivacyIncident:
        inc_id = f"pinc_{secrets.token_hex(8)}"
        inc = PrivacyIncident(
            id=inc_id,
            title=title,
            severity=severity,
            stage=PrivacyIncidentStage.DETECTED,
            affected_subjects_count=affected_count
        )
        self._incidents[inc_id] = inc
        return inc

    def execute_containment(self, incident_id: str, action: str) -> tuple[bool, PrivacyIncident]:
        inc = self._incidents.get(incident_id)
        if not inc:
            raise ValueError("INCIDENT_NOT_FOUND")

        inc.containment_actions.append(action)
        inc.stage = PrivacyIncidentStage.CONTAINED
        inc.contained_at = time.time()
        return True, inc

    def close_incident(self, incident_id: str) -> tuple[bool, PrivacyIncident]:
        inc = self._incidents.get(incident_id)
        if not inc:
            raise ValueError("INCIDENT_NOT_FOUND")

        inc.stage = PrivacyIncidentStage.CLOSED
        inc.closed_at = time.time()
        return True, inc
