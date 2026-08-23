"""
DigiIn Production Infrastructure — Deployment Orchestrator & Fast Rollback Engine
Manages canary rollouts (5% -> 25% -> 50% -> 100%), automated health checks, and instant rollback to immutable artifact digests.
"""

from __future__ import annotations

import time


class DeploymentStage:
    CANARY_5 = 5
    CANARY_25 = 25
    CANARY_50 = 50
    FULL_100 = 100

class DeploymentRecord:
    def __init__(
        self,
        deployment_id: str,
        version: str,
        artifact_digest: str,
        target_environment: str = "PRODUCTION",
        stage: int = DeploymentStage.CANARY_5,
        status: str = "IN_PROGRESS"
    ):
        self.deployment_id = deployment_id
        self.version = version
        self.artifact_digest = artifact_digest
        self.target_environment = target_environment
        self.stage = stage
        self.status = status
        self.created_at = time.time()
        self.completed_at: float | None = None
        self.rollback_digest: str | None = None

class DeploymentOrchestrator:
    def __init__(self):
        self._current_stable_digest = "sha256:digest_stable_v1_0_0_baseline"
        self._current_stable_version = "1.0.0"
        self._active_deployment: DeploymentRecord | None = None

    def start_deployment(
        self,
        deployment_id: str,
        new_version: str,
        new_artifact_digest: str
    ) -> DeploymentRecord:
        record = DeploymentRecord(
            deployment_id=deployment_id,
            version=new_version,
            artifact_digest=new_artifact_digest,
            stage=DeploymentStage.CANARY_5,
            status="CANARY_5_PERCENT"
        )
        record.rollback_digest = self._current_stable_digest
        self._active_deployment = record
        return record

    def advance_canary_stage(self, health_ok: bool) -> tuple[bool, str | None, DeploymentRecord | None]:
        if not self._active_deployment:
            return False, "NO_ACTIVE_DEPLOYMENT", None

        if not health_ok:
            # Auto-rollback on health failure
            return self.trigger_rollback("Health check gate failed during canary progression.")

        stage = self._active_deployment.stage
        if stage == DeploymentStage.CANARY_5:
            self._active_deployment.stage = DeploymentStage.CANARY_25
            self._active_deployment.status = "CANARY_25_PERCENT"
        elif stage == DeploymentStage.CANARY_25:
            self._active_deployment.stage = DeploymentStage.CANARY_50
            self._active_deployment.status = "CANARY_50_PERCENT"
        elif stage == DeploymentStage.CANARY_50:
            self._active_deployment.stage = DeploymentStage.FULL_100
            self._active_deployment.status = "DEPLOYED_100_PERCENT"
            self._active_deployment.completed_at = time.time()
            self._current_stable_digest = self._active_deployment.artifact_digest
            self._current_stable_version = self._active_deployment.version

        return True, None, self._active_deployment

    def trigger_rollback(self, reason: str) -> tuple[bool, str, DeploymentRecord]:
        """Instantly switch traffic back to the previous stable immutable artifact digest."""
        if not self._active_deployment:
            raise RuntimeError("NO_DEPLOYMENT_TO_ROLLBACK")

        self._active_deployment.status = "ROLLED_BACK"
        self._active_deployment.completed_at = time.time()
        msg = f"ROLLBACK_EXECUTED: Restored stable digest '{self._current_stable_digest}'. Reason: {reason}"
        return True, msg, self._active_deployment

    @property
    def current_active_digest(self) -> str:
        return self._current_stable_digest
