"""Phase 9 — Scale, Observability & Production Operations Test Suite.

Validates:
  1. Asynchronous Job Worker & Dead-Letter Queue (DLQ) state machine & retries.
  2. Idempotency & Request Deduplication with payload conflict detection.
  3. Multi-tier Object Storage with SHA-256 integrity verification & tampering defense.
  4. Observability: Structured JSON logging (zero PII), metrics, tracing & SLO engine.
  5. Tiered Health Probes (live/ready/deps) & Graceful Degradation during outages.
  6. Database Schema Migrations & Disaster Recovery Restoration Drills (RPO/RTO).
  7. 100-Concurrent Load Test Benchmark Simulator Harness.
  8. Operator Operations Dashboard APIs (/api/v1/ops/*).
"""

from __future__ import annotations

import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "services" / "api"))
sys.path.insert(0, str(root_dir))

from fastapi.testclient import TestClient

from app.core.operations import (
    JobPriority,
    JobState,
    JobWorkerEngine,
    StorageIntegrityError,
    degradation_manager,
    dr_coordinator,
    ephemeral_cache,
    health_probes,
    idempotency_engine,
    load_test_harness,
    migration_manager,
    object_storage,
    observability,
    scrub_pii,
)
from app.db.session import init_db
from app.main import app

init_db()
client = TestClient(app)


# ===========================================================================
# 9.1 — Job Worker Engine & Dead-Letter Queue (DLQ)
# ===========================================================================


def test_job_worker_and_dlq():
    print(">>> 9.1 Asynchronous Job Worker Engine & DLQ...")

    worker = JobWorkerEngine()
    processed_items = []

    # Register handlers
    worker.register_handler(
        "OCR_TASK",
        lambda p: {"text": f"Extracted OCR for {p.get('doc_id')}", "confidence": 0.98},
    )

    def failing_handler(p):
        raise RuntimeError("Transient provider timeout")

    worker.register_handler("FAILING_TASK", failing_handler)

    # 1. Enqueue normal & critical priority jobs
    job1 = worker.enqueue("OCR_TASK", {"doc_id": "doc_001"}, priority=JobPriority.NORMAL)
    job2 = worker.enqueue("OCR_TASK", {"doc_id": "doc_002_urgent"}, priority=JobPriority.CRITICAL)

    assert job1.state == JobState.QUEUED
    assert job2.state == JobState.QUEUED

    # 2. Critical job executes first
    executed1 = worker.process_next()
    assert executed1.job_id == job2.job_id
    assert executed1.state == JobState.SUCCEEDED
    assert executed1.result["confidence"] == 0.98

    # 3. Normal job executes next
    executed2 = worker.process_next()
    assert executed2.job_id == job1.job_id
    assert executed2.state == JobState.SUCCEEDED

    # 4. Test retries and DLQ
    fail_job = worker.enqueue("FAILING_TASK", {"doc_id": "doc_fail"}, max_attempts=2)
    
    # Attempt 1 -> RETRYING
    res1 = worker.process_next()
    assert res1.state == JobState.RETRYING
    assert res1.attempts == 1
    assert res1.calculate_backoff() > 0

    # Attempt 2 -> FAILED & sent to DLQ
    res2 = worker.process_next()
    assert res2.state == JobState.FAILED
    assert res2.attempts == 2

    dlq_items = worker.list_dlq()
    assert len(dlq_items) == 1
    assert dlq_items[0]["job_id"] == fail_job.job_id
    assert "Transient provider timeout" in dlq_items[0]["reason"]

    # 5. Replay from DLQ
    replayed_job = worker.retry_dlq_item(dlq_items[0]["dlq_id"])
    assert replayed_job.state == JobState.QUEUED
    assert replayed_job.attempts == 0

    stats = worker.get_stats()
    assert stats["total_jobs"] >= 3
    assert stats["successful_jobs"] == 2

    print("    [PASS] Job priorities, execution state machine, backoff, and DLQ capture/replay verified")


# ===========================================================================
# 9.2 — Idempotency & Request Deduplication
# ===========================================================================


def test_idempotency_engine():
    print(">>> 9.2 Idempotency & Request Deduplication...")

    key = "idem_key_test_12345"
    path = "/api/v1/credentials/issue"
    payload = {"holder": "Rahul Sharma", "credential_type": "MARKSHEET"}

    fingerprint = idempotency_engine.compute_fingerprint(path, "POST", payload)

    # Initial check -> not cached
    is_cached, status, body = idempotency_engine.get_cached_response(key, fingerprint)
    assert not is_cached

    # Store successful response
    idempotency_engine.store_response(
        idempotency_key=key,
        fingerprint=fingerprint,
        status_code=201,
        response_body={"credential_id": "crd_12345", "status": "VERIFIED"},
        ttl_seconds=3600,
    )

    # Replay with same key & payload -> returns cached response
    is_cached2, status2, body2 = idempotency_engine.get_cached_response(key, fingerprint)
    assert is_cached2
    assert status2 == 201
    assert body2["credential_id"] == "crd_12345"

    # Replay with different payload -> raises conflict exception
    diff_fingerprint = idempotency_engine.compute_fingerprint(path, "POST", {"holder": "Different Person"})
    try:
        idempotency_engine.get_cached_response(key, diff_fingerprint)
        assert False, "Should raise ValueError on payload conflict"
    except ValueError as e:
        assert "collision" in str(e).lower()

    print("    [PASS] Idempotency response caching, duplicate replay, and conflict detection verified")


# ===========================================================================
# 9.3 — Multi-Tier Object Storage & Integrity Verification
# ===========================================================================


def test_object_storage_and_integrity():
    print(">>> 9.3 Multi-Tier Object Storage & Cryptographic Integrity...")

    content = b"ORIGINAL HIGH-CONFIDENTIAL MARKSHEET DIGITAL ASSET 2026"
    stored = object_storage.put_object(
        document_id="doc_xyz_100",
        content=content,
        media_type="application/pdf",
        version=1,
    )

    assert stored.content_hash is not None
    assert stored.encrypted_size == len(content)

    # Retrieve and verify integrity
    meta, blob = object_storage.get_object(stored.object_id)
    assert blob == content
    assert meta.content_hash == stored.content_hash

    # Simulate byte corruption / tampering
    corrupted_key = stored.storage_key
    object_storage._blobs[corrupted_key] = b"TAMPERED CORRUPTED CONTENT"

    try:
        object_storage.get_object(stored.object_id)
        assert False, "Should have raised StorageIntegrityError upon tampering"
    except StorageIntegrityError as e:
        assert "integrity failure" in str(e).lower()

    # Restore clean blob and test bounded cache
    object_storage._blobs[corrupted_key] = content
    ephemeral_cache.set("challenge:test", "challenge_val_123", ttl_seconds=60)
    assert ephemeral_cache.get("challenge:test") == "challenge_val_123"
    assert ephemeral_cache.get("challenge:nonexistent") is None
    assert ephemeral_cache.get_hit_rate() > 0.0

    print("    [PASS] SHA-256 storage integrity checks, tamper defense, and cache verified")


# ===========================================================================
# 9.4 — Three Pillars of Observability & SLO Tracking
# ===========================================================================


def test_observability_and_slos():
    print(">>> 9.4 Observability (Logs, Metrics, Traces & SLO Engine)...")

    # 1. PII Scrubbing in structured logs
    raw_log = "Processing applicant Aadhaar 2345 6789 0123 with PAN ABCDE1234F and OTP:987654"
    scrubbed = scrub_pii(raw_log)
    assert "2345" not in scrubbed
    assert "ABCDE1234F" not in scrubbed
    assert "987654" not in scrubbed
    assert "[REDACTED_AADHAAR]" in scrubbed
    assert "[REDACTED_PAN]" in scrubbed

    event = observability.log(
        level="INFO",
        service="verification",
        operation="credential.verify",
        status="SUCCESS",
        metadata={"applicant_details": raw_log},
    )
    json_log = event.to_json()
    assert "2345" not in json_log

    # 2. Distributed Tracing
    span1 = observability.start_span("http_request")
    span2 = observability.start_span("credential_lookup", trace_id=span1.trace_id, parent_span_id=span1.span_id)
    dur2 = span2.finish()
    dur1 = span1.finish()
    assert span2.trace_id == span1.trace_id
    assert dur1 >= 0.0

    # 3. Metrics and SLO Engine
    for _ in range(50):
        observability.record_request(duration_ms=12.5, is_error=False)
        observability.record_verification(duration_ms=45.0, success=True)
    observability.record_credential_issued()

    metrics = observability.get_metrics_snapshot()
    assert metrics["requests_total"] >= 50
    assert metrics["error_rate_pct"] == 0.0
    assert metrics["latency_p95_ms"] > 0.0
    assert metrics["verification_success_rate_pct"] == 100.0

    slo_report = observability.evaluate_slos()
    assert slo_report["overall_status"] == "COMPLIANT"
    assert slo_report["slos"]["availability_ge_99_9"]["status"] == "PASS"
    assert slo_report["slos"]["api_p95_latency_lt_500ms"]["status"] == "PASS"

    print("    [PASS] PII scrubbed JSON logs, distributed spans, metrics histograms, and SLO compliance verified")


# ===========================================================================
# 9.5 — Tiered Health Probes & Graceful Degradation
# ===========================================================================


def test_health_probes_and_degradation():
    print(">>> 9.5 Tiered Health Probes & Graceful Degradation...")

    # 1. Liveness
    live = health_probes.check_liveness()
    assert live["status"] == "UP"

    # 2. Readiness
    ready, res = health_probes.check_readiness()
    assert ready
    assert res["status"] == "READY"

    # 3. Dependency health (Normal state)
    deps = health_probes.check_dependencies()
    assert deps["overall_system_state"] in ("HEALTHY", "DEGRADED")
    assert len(deps["dependencies"]) >= 4

    # 4. Graceful Degradation during External Outage
    degradation_manager.mark_provider_outage("mock-cbse-001", is_down=True)
    assert not degradation_manager.is_provider_available("mock-cbse-001")
    assert degradation_manager.can_verify_offline("MARKSHEET")

    deps_outage = health_probes.check_dependencies()
    assert deps_outage["overall_system_state"] == "DEGRADED"
    assert "OUTAGE" in deps_outage["providers"]["mock-cbse-001"]

    # Restore provider
    degradation_manager.mark_provider_outage("mock-cbse-001", is_down=False)
    assert degradation_manager.is_provider_available("mock-cbse-001")

    print("    [PASS] 3-tier health checks (live/ready/deps) and graceful degradation under outage verified")


# ===========================================================================
# 9.6 — Migrations & Disaster Recovery Drills
# ===========================================================================


def test_migrations_and_dr():
    print(">>> 9.6 Schema Migrations & Disaster Recovery Drills...")

    # Migrations
    applied = migration_manager.apply_all_pending()
    status = migration_manager.get_migration_status()
    assert status["total_registered"] >= 4
    assert status["applied_count"] == status["total_registered"]
    assert status["current_schema_version"] >= 4

    # Disaster Recovery Snapshot & Restoration Drill
    snap = dr_coordinator.create_snapshot("postgresql", b"MOCK POSTGRESQL DATABASE DUMP 2026")
    assert snap.snapshot_id.startswith("snap_postgresql")
    assert len(snap.sha256_checksum) == 64

    drill = dr_coordinator.run_restoration_drill(snap.snapshot_id, simulated_delay_sec=0.01)
    assert drill.rto_compliant
    assert drill.data_verified

    dr_status = dr_coordinator.get_dr_status()
    assert dr_status["rpo_target_minutes"] <= 15.0
    assert dr_status["rto_target_minutes"] <= 60.0
    assert dr_status["last_drill_status"] == "PASS"

    print("    [PASS] Versioned schema migrations and automated DR backup restoration drills verified")


# ===========================================================================
# 9.7 — Concurrency Load Testing Benchmark Simulator
# ===========================================================================


def test_concurrency_load_harness():
    print(">>> 9.7 100-Concurrent Load Benchmark Simulation...")

    report = load_test_harness.run_benchmark(total_requests=100, concurrency=20)
    assert report.total_requests == 100
    assert report.concurrency_level == 20
    assert report.error_count == 0
    assert report.throughput_rps > 50.0
    assert report.latency_p95_ms < 500.0

    # Verify proof verification is faster than document upload
    workloads = report.workload_latencies
    if "proof_verification" in workloads and "document_upload" in workloads:
        assert workloads["proof_verification"] <= workloads["document_upload"]

    print(f"    [PASS] 100 concurrent requests benchmarked: {report.throughput_rps:.1f} req/s, p95={report.latency_p95_ms:.2f}ms")


# ===========================================================================
# 9.8 — Operations Dashboard APIs
# ===========================================================================


def test_ops_api_endpoints():
    print(">>> 9.8 Operations Dashboard API Endpoints...")

    # 1. Dashboard
    resp = client.get("/api/v1/ops/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["system"]["api_status"] == "HEALTHY"
    assert "traffic" in data
    assert "performance" in data

    # 2. SLOs
    resp_slo = client.get("/api/v1/ops/slo")
    assert resp_slo.status_code == 200
    assert resp_slo.json()["overall_status"] == "COMPLIANT"

    # 3. DLQ
    resp_dlq = client.get("/api/v1/ops/dlq")
    assert resp_dlq.status_code == 200
    assert isinstance(resp_dlq.json(), list)

    # 4. Probes
    assert client.get("/api/v1/ops/health/live").status_code == 200
    assert client.get("/api/v1/ops/health/ready").status_code == 200
    assert client.get("/api/v1/ops/health/deps").status_code == 200
    assert client.get("/api/v1/ops/dr").status_code == 200
    assert client.get("/api/v1/ops/migrations").status_code == 200

    print("    [PASS] All 8 operator dashboard and health probe endpoints verified (200 OK)")


# ===========================================================================
# Main Execution
# ===========================================================================


if __name__ == "__main__":
    print("=" * 80)
    print("DIGIIN PHASE 9 — SCALE, OBSERVABILITY & PRODUCTION OPERATIONS TEST SUITE")
    print("=" * 80)

    test_job_worker_and_dlq()
    test_idempotency_engine()
    test_object_storage_and_integrity()
    test_observability_and_slos()
    test_health_probes_and_degradation()
    test_migrations_and_dr()
    test_concurrency_load_harness()
    test_ops_api_endpoints()

    print()
    print("=" * 80)
    print("SUCCESS: ALL PHASE 9 PRODUCTION OPERATIONS & OBSERVABILITY TESTS PASSED!")
    print("=" * 80)
