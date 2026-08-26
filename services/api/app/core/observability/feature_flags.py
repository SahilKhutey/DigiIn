"""
DigiIn Observability Subsystem — Feature Flags & Canary Rollouts
Allows controlled gradual rollout and instant kill-switches / maintenance mode per subsystem.
"""

from __future__ import annotations

import hashlib


class FeatureFlag:
    def __init__(
        self,
        key: str,
        enabled: bool = False,
        rollout_percentage: int = 100,
        environment: str = "PRODUCTION",
        maintenance_mode: bool = False
    ):
        self.key = key
        self.enabled = enabled
        self.rollout_percentage = rollout_percentage
        self.environment = environment
        self.maintenance_mode = maintenance_mode

    def is_enabled_for_user(self, user_id: str) -> bool:
        if not self.enabled or self.maintenance_mode:
            return False
        if self.rollout_percentage >= 100:
            return True
        if self.rollout_percentage <= 0:
            return False

        # Deterministic hash bucket (0-99) using SHA-256
        bucket = int(hashlib.sha256(f"{self.key}:{user_id}".encode()).hexdigest()[:4], 16) % 100
        return bucket < self.rollout_percentage

class FeatureFlagManager:
    def __init__(self):
        self._flags: dict[str, FeatureFlag] = {}
        self._seed_default_flags()

    def _seed_default_flags(self):
        self.set_flag("FF_NEW_PROVIDER_GATEWAY", enabled=True, rollout_percentage=100)
        self.set_flag("FF_ED25519_PROOF_V2", enabled=True, rollout_percentage=100)
        self.set_flag("FF_CANARY_EXPERIMENTAL_OCR", enabled=True, rollout_percentage=25)

    def set_flag(
        self,
        key: str,
        enabled: bool = True,
        rollout_percentage: int = 100,
        environment: str = "PRODUCTION",
        maintenance_mode: bool = False
    ):
        self._flags[key] = FeatureFlag(
            key=key,
            enabled=enabled,
            rollout_percentage=rollout_percentage,
            environment=environment,
            maintenance_mode=maintenance_mode
        )

    def is_feature_enabled(self, key: str, user_id: str = "anonymous") -> bool:
        flag = self._flags.get(key)
        if not flag:
            return False
        return flag.is_enabled_for_user(user_id)
