"""
DigiIn Trust Network & Interoperability — Trust Security & Anti-Enumeration Guard
Protects against blind citizen account existence probes, credential scraping, and suspicious verifier spikes.
"""

from __future__ import annotations

import time
from typing import Any


class AntiEnumerationGuard:
    def __init__(self, max_probes_per_window: int = 10, window_seconds: float = 60.0):
        self.max_probes = max_probes_per_window
        self.window_seconds = window_seconds
        self._probes: dict[str, list[float]] = {}

    def record_and_check_probe(self, client_ip: str, subject_query: str) -> tuple[bool, str]:
        now = time.time()
        if client_ip not in self._probes:
            self._probes[client_ip] = []

        # Prune old timestamps
        cutoff = now - self.window_seconds
        self._probes[client_ip] = [t for t in self._probes[client_ip] if t > cutoff]

        if len(self._probes[client_ip]) >= self.max_probes:
            return False, "RATE_LIMIT_ENUMERATION_ATTACK_DETECTED: Excessive subject existence queries from IP."

        self._probes[client_ip].append(now)
        return True, "PROBE_ALLOWED"

class TrustNetworkMonitor:
    def __init__(self):
        self._events: list[dict[str, Any]] = []

    def record_event(self, event_type: str, actor_id: str, payload: dict[str, Any]):
        self._events.append({
            "timestamp": time.time(),
            "eventType": event_type,
            "actorId": actor_id,
            "payload": payload
        })

    def get_network_kpis(self) -> dict[str, Any]:
        total_events = len(self._events)
        issued = sum(1 for e in self._events if e["eventType"] == "claim.issued")
        presented = sum(1 for e in self._events if e["eventType"] == "claim.presented")
        revoked = sum(1 for e in self._events if e["eventType"] == "claim.revoked")

        return {
            "totalNetworkEvents": total_events,
            "claimsIssuedCount": issued,
            "claimsPresentedCount": presented,
            "claimsRevokedCount": revoked,
        }
