"""
DigiIn Observability Subsystem — Alert & Incident Lifecycle Management
Evaluates operational alerting rules across P0-P3 severity tiers and tracks incident timelines.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Alert:
    id: str
    severity: str  # "P0" | "P1" | "P2" | "P3"
    title: str
    description: str
    subsystem: str
    triggered_at: float = field(default_factory=time.time)
    resolved_at: float | None = None
    status: str = "FIRING"  # "FIRING" | "RESOLVED"

@dataclass
class Incident:
    id: str
    severity: str
    title: str
    status: str = "OPEN"  # "OPEN" | "INVESTIGATING" | "MITIGATING" | "RESOLVED"
    started_at: float = field(default_factory=time.time)
    resolved_at: float | None = None
    affected_services: list[str] = field(default_factory=list)
    timeline: list[dict[str, Any]] = field(default_factory=list)

    def add_timeline_event(self, note: str, actor: str = "OPERATOR"):
        self.timeline.append({
            "timestamp": time.time(),
            "note": note,
            "actor": actor
        })

    def transition_status(self, new_status: str, note: str = ""):
        self.status = new_status
        if note:
            self.add_timeline_event(f"Status changed to {new_status}: {note}")
        if new_status == "RESOLVED":
            self.resolved_at = time.time()

class AlertAndIncidentManager:
    def __init__(self):
        self.alerts: list[Alert] = []
        self.incidents: dict[str, Incident] = []
        self._incidents_map: dict[str, Incident] = {}

    def fire_alert(self, severity: str, title: str, description: str, subsystem: str) -> Alert:
        alert_id = f"alt_{secrets.token_hex(8)}"
        alert = Alert(
            id=alert_id,
            severity=severity,
            title=title,
            description=description,
            subsystem=subsystem
        )
        self.alerts.append(alert)

        # Automatic P0/P1 Incident creation
        if severity in ("P0", "P1"):
            self.create_incident_from_alert(alert)
        return alert

    def create_incident_from_alert(self, alert: Alert) -> Incident:
        inc_id = f"inc_{secrets.token_hex(8)}"
        inc = Incident(
            id=inc_id,
            severity=alert.severity,
            title=f"Incident: {alert.title}",
            affected_services=[alert.subsystem],
            timeline=[{"timestamp": time.time(), "note": f"Triggered by alert {alert.id}: {alert.description}", "actor": "SYSTEM"}]
        )
        self._incidents_map[inc_id] = inc
        return inc

    def get_incident(self, incident_id: str) -> Incident | None:
        return self._incidents_map.get(incident_id)

    def list_open_incidents(self) -> list[Incident]:
        return [inc for inc in self._incidents_map.values() if inc.status != "RESOLVED"]
