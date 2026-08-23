"""
DigiIn Long-Term Infrastructure — Platform Governance Model
Implements formal governance committees (Policy, Security, Privacy, Technical Standards) and versioned policy management.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


class GovernanceCommittee:
    POLICY_COMMITTEE = "POLICY_COMMITTEE"
    SECURITY_COMMITTEE = "SECURITY_COMMITTEE"
    PRIVACY_COMMITTEE = "PRIVACY_COMMITTEE"
    TECHNICAL_STANDARDS = "TECHNICAL_STANDARDS"

@dataclass
class VersionedPolicy:
    policy_id: str
    committee: str
    version: str
    rules: dict[str, Any]
    effective_from: float = field(default_factory=time.time)
    superseded_at: float | None = None
    status: str = "ACTIVE"

class PlatformGovernanceEngine:
    def __init__(self):
        self._policies: dict[str, VersionedPolicy] = {}
        self._seed_default_policies()

    def _seed_default_policies(self):
        p1 = VersionedPolicy(
            policy_id="pol_trust_baseline",
            committee=GovernanceCommittee.POLICY_COMMITTEE,
            version="1.0.0",
            rules={"min_assurance_for_education": "A3_HIGH_ASSURANCE", "max_consent_days": 30}
        )
        self._policies[p1.policy_id] = p1

    def publish_policy_version(
        self,
        committee: str,
        policy_id: str,
        new_version: str,
        rules: dict[str, Any]
    ) -> VersionedPolicy:
        old_pol = self._policies.get(policy_id)
        if old_pol:
            old_pol.status = "SUPERSEDED"
            old_pol.superseded_at = time.time()

        new_pol = VersionedPolicy(
            policy_id=policy_id,
            committee=committee,
            version=new_version,
            rules=rules
        )
        self._policies[policy_id] = new_pol
        return new_pol

    def get_policy(self, policy_id: str) -> VersionedPolicy | None:
        return self._policies.get(policy_id)
