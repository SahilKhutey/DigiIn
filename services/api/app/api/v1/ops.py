"""Phase 9 API Router — Operator & Production Operations Dashboard.

Endpoints:
  - GET  /api/v1/ops/dashboard      -> Real-time system operational metrics & dashboard
  - GET  /api/v1/ops/slo            -> Measurable SLO compliance scorecard
  - GET  /api/v1/ops/dlq            -> Dead-Letter Queue inspection
  - POST /api/v1/ops/dlq/{id}/retry -> Re-enqueue failed job from DLQ
  - GET  /api/v1/ops/health/live    -> Liveness probe
  - GET  /api/v1/ops/health/ready   -> Readiness probe
  - GET  /api/v1/ops/health/deps    -> Dependency health breakdown
  - GET  /api/v1/ops/dr             -> Disaster recovery status & RPO/RTO posture
  - GET  /api/v1/ops/migrations     -> Database schema migration status
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Response

from app.core.operations.disaster_recovery import dr_coordinator
from app.core.operations.health_probes import health_probes
from app.core.operations.job_worker import job_worker
from app.core.operations.migrations import migration_manager
from app.core.operations.observability import observability

router = APIRouter(prefix="/ops", tags=["operations"])


@router.get("/dashboard")
def get_ops_dashboard() -> dict[str, Any]:
    """Returns comprehensive real-time system metrics for the operator dashboard."""
    metrics = observability.get_metrics_snapshot()
    job_stats = job_worker.get_stats()
    dep_health = health_probes.check_dependencies()

    return {
        "system": {
            "api_status": "HEALTHY",
            "database_status": dep_health["dependencies"][0]["status"],
            "queue_status": "HEALTHY" if job_stats["dlq_count"] < 10 else "DEGRADED",
            "storage_status": dep_health["dependencies"][3]["status"],
            "providers_active": sum(
                1 for v in dep_health["providers"].values() if v == "UP"
            ),
            "providers_total": len(dep_health["providers"]),
        },
        "traffic": {
            "requests_total": metrics["requests_total"],
            "verifications_total": metrics["verifications_total"],
            "credentials_issued": metrics["credentials_issued"],
            "pending_jobs": job_stats["queue_depth"],
            "failed_jobs": job_stats["failed_jobs"],
            "dlq_count": job_stats["dlq_count"],
        },
        "performance": {
            "latency_p50_ms": metrics["latency_p50_ms"],
            "latency_p95_ms": metrics["latency_p95_ms"],
            "latency_p99_ms": metrics["latency_p99_ms"],
            "verification_latency_p95_ms": metrics["verification_latency_p95_ms"],
            "error_rate_pct": metrics["error_rate_pct"],
        },
        "providers": dep_health["providers"],
    }


@router.get("/slo")
def get_slo_report() -> dict[str, Any]:
    """Returns the current SLO compliance scorecard."""
    return observability.evaluate_slos()


@router.get("/dlq")
def list_dead_letter_queue() -> list[dict[str, Any]]:
    """Lists dead-letter queue records for operator investigation."""
    return job_worker.list_dlq()


@router.post("/dlq/{dlq_id}/retry")
def retry_dlq_job(dlq_id: str) -> dict[str, Any]:
    """Replays a failed job from the Dead-Letter Queue."""
    job = job_worker.retry_dlq_item(dlq_id)
    if not job:
        raise HTTPException(status_code=404, detail="DLQ record not found.")
    return {
        "status": "re-enqueued",
        "dlq_id": dlq_id,
        "job_id": job.job_id,
        "job_state": job.state.value,
    }


@router.get("/health/live")
def liveness_probe() -> dict[str, Any]:
    """Liveness probe: verifies the process is responsive."""
    return health_probes.check_liveness()


@router.get("/health/ready")
def readiness_probe(response: Response) -> dict[str, Any]:
    """Readiness probe: validates critical dependencies before serving traffic."""
    ready, result = health_probes.check_readiness()
    if not ready:
        response.status_code = 503
    return result


@router.get("/health/deps")
def dependency_health() -> dict[str, Any]:
    """Detailed dependency health breakdown."""
    return health_probes.check_dependencies()


@router.get("/dr")
def disaster_recovery_status() -> dict[str, Any]:
    """Disaster recovery and RPO/RTO compliance status."""
    return dr_coordinator.get_dr_status()


@router.get("/migrations")
def database_migrations_status() -> dict[str, Any]:
    """Database schema migration status."""
    return migration_manager.get_migration_status()
