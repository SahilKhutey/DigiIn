"""
DigiIn National Scale — Security Operations Center (SOC)
Centralizes security event ingestion, automated threat detection rules, and incident triage.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any


class ThreatSeverity:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class SecurityEvent:
    id: str
    event_type: str
    severity: str
    actor_id: str
    organization_id: str
    details: dict[str, Any]
    timestamp: float = field(default_factory=time.time)

@dataclass
class SecurityAlert:
    alert_id: str
    rule_name: str
    severity: str
    target_entity: str
    description: str
    status: str = "OPEN"  # "OPEN" | "INVESTIGATING" | "CONTAINED" | "RESOLVED"
    created_at: float = field(default_factory=time.time)

class SecurityOperationsCenter:
    def __init__(self):
        self._events: list[SecurityEvent] = []
        self._alerts: dict[str, SecurityAlert] = {}

    def ingest_event(
        self,
        event_type: str,
        severity: str,
        actor_id: str,
        organization_id: str,
        details: dict[str, Any]
    ) -> SecurityEvent:
        eid = f"sec_{secrets.token_hex(8)}"
        evt = SecurityEvent(
            id=eid,
            event_type=event_type,
            severity=severity,
            actor_id=actor_id,
            organization_id=organization_id,
            details=details
        )
        self._events.append(evt)
        self._evaluate_detection_rules(evt)
        return evt

    def _evaluate_detection_rules(self, evt: SecurityEvent):
        # Detection Rule 1: Repeated Token Replay / Key Abuse
        if evt.event_type == "TOKEN_REPLAY_ATTEMPT" or evt.severity == ThreatSeverity.CRITICAL:
            aid = f"alt_{secrets.token_hex(8)}"
            self._alerts[aid] = SecurityAlert(
                alert_id=aid,
                rule_name="CRITICAL_TOKEN_REPLAY_OR_ABUSE",
                severity=ThreatSeverity.CRITICAL,
                target_entity=evt.organization_id or evt.actor_id,
                description=f"Critical threat event detected from actor {evt.actor_id} in org {evt.organization_id}"
            )

    def list_open_alerts(self) -> list[SecurityAlert]:
        return [a for a in self._alerts.values() if a.status != "RESOLVED"]
