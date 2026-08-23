"""
DigiIn Trust Network Expansion — Fraud & Abuse Intelligence
Monitors request velocities, suspicious verification bursts, and automated state transitions (NORMAL -> THROTTLED -> SUSPENDED).
"""

from __future__ import annotations

import time


class AbuseRiskState:
    NORMAL = "NORMAL"
    MONITORED = "MONITORED"
    THROTTLED = "THROTTLED"
    RESTRICTED = "RESTRICTED"
    SUSPENDED = "SUSPENDED"

class FraudAbuseIntelligence:
    def __init__(self, burst_threshold_per_min: int = 100, critical_burst_threshold: int = 500):
        self.burst_threshold = burst_threshold_per_min
        self.critical_threshold = critical_burst_threshold
        self._request_windows: dict[str, list[float]] = {}
        self._entity_states: dict[str, str] = {}

    def track_request(self, entity_id: str) -> tuple[str, bool]:
        """Returns (current_abuse_state, is_request_allowed)."""
        now = time.time()
        if entity_id not in self._request_windows:
            self._request_windows[entity_id] = []

        # Prune older than 60s
        cutoff = now - 60.0
        self._request_windows[entity_id] = [t for t in self._request_windows[entity_id] if t > cutoff]
        self._request_windows[entity_id].append(now)

        count = len(self._request_windows[entity_id])
        if count > self.critical_threshold:
            self._entity_states[entity_id] = AbuseRiskState.SUSPENDED
            return AbuseRiskState.SUSPENDED, False
        elif count > self.burst_threshold:
            self._entity_states[entity_id] = AbuseRiskState.THROTTLED
            return AbuseRiskState.THROTTLED, False
        elif count > (self.burst_threshold // 2):
            self._entity_states[entity_id] = AbuseRiskState.MONITORED
            return AbuseRiskState.MONITORED, True
        else:
            self._entity_states[entity_id] = AbuseRiskState.NORMAL
            return AbuseRiskState.NORMAL, True

    def get_state(self, entity_id: str) -> str:
        return self._entity_states.get(entity_id, AbuseRiskState.NORMAL)
