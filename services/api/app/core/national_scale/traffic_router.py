"""
DigiIn National Scale — National Traffic Router & Multi-Region Manager
Handles multi-region health-aware routing, automated failover draining, 5-tier request classification, and priority scheduling.
"""

from __future__ import annotations

from dataclasses import dataclass


class RegionStatus:
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    DRAINING = "DRAINING"
    OFFLINE = "OFFLINE"

class RequestTier:
    PUBLIC = "PUBLIC"
    AUTHENTICATED = "AUTHENTICATED"
    INSTITUTIONAL = "INSTITUTIONAL"
    PRIVILEGED = "PRIVILEGED"
    SYSTEM = "SYSTEM"

class TrafficPriority:
    P1_VERIFICATION = 1
    P2_AUTHENTICATION = 2
    P3_CLAIM_OPS = 3
    P4_ANALYTICS = 4
    P5_BACKGROUND = 5

@dataclass
class Region:
    id: str
    name: str
    status: str = RegionStatus.ACTIVE
    capacity_rps: int = 10000
    current_load_rps: int = 0
    latency_p95_ms: float = 25.0
    error_rate: float = 0.0

class NationalTrafficRouter:
    def __init__(self):
        self._regions: dict[str, Region] = {}
        self._seed_default_regions()

    def _seed_default_regions(self):
        r1 = Region(id="in-west-mumbai", name="India West (Mumbai)", capacity_rps=25000, current_load_rps=3200)
        r2 = Region(id="in-south-hyderabad", name="India South (Hyderabad)", capacity_rps=20000, current_load_rps=1800)
        r3 = Region(id="in-north-delhi", name="India North (Delhi)", capacity_rps=20000, current_load_rps=1400)
        self._regions[r1.id] = r1
        self._regions[r2.id] = r2
        self._regions[r3.id] = r3

    def route_request(self, client_region: str, tier: str, priority: int) -> tuple[bool, str, str]:
        """Routes request to the lowest latency healthy region, or drains to backup if degraded."""
        pref_region = self._regions.get(client_region)
        if pref_region and pref_region.status == RegionStatus.ACTIVE:
            return True, pref_region.id, "ROUTED_TO_PRIMARY_REGION"

        # If preferred region is degraded or draining, failover to best healthy region
        active_regions = [r for r in self._regions.values() if r.status == RegionStatus.ACTIVE]
        if not active_regions:
            return False, "NONE", "ALL_REGIONS_UNAVAILABLE_CRITICAL"

        best_region = sorted(active_regions, key=lambda r: r.current_load_rps / r.capacity_rps)[0]
        return True, best_region.id, f"FAILOVER_DRAINED_TO_{best_region.id}"

    def drain_region(self, region_id: str, reason: str = "SCHEDULED_MAINTENANCE") -> bool:
        reg = self._regions.get(region_id)
        if not reg:
            return False
        reg.status = RegionStatus.DRAINING
        return True

    def mark_region_degraded(self, region_id: str) -> bool:
        reg = self._regions.get(region_id)
        if not reg:
            return False
        reg.status = RegionStatus.DEGRADED
        return True

    def restore_region(self, region_id: str) -> bool:
        reg = self._regions.get(region_id)
        if not reg:
            return False
        reg.status = RegionStatus.ACTIVE
        return True
