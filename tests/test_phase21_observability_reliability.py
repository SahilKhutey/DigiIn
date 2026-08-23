"""
DigiIn Automated Observability, Reliability & Operations Test Suite (Phase 21)
Validates structured logging with PII scrubbing, metrics, distributed tracing, health probes, alerting, DLQ, backup verification, and feature flags.
"""

import sys
import os
import json
import hashlib

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.observability import (
    StructuredLogger,
    MetricsCollector,
    DistributedTracer,
    HealthProbeManager,
    AlertAndIncidentManager,
    DeadLetterQueueService,
    BackupVerifier,
    FeatureFlagManager,
    OperationsDashboardService,
)

def test_structured_logging_and_pii_scrubbing():
    print(">>> 1. Testing Structured Logging & Automatic PII Scrubbing...")
    logger = StructuredLogger(service_name="api-gateway")

    # Log containing sensitive data: password, bearer token, Aadhaar number
    event = logger.info(
        event="user.authentication.attempt",
        request_id="req_0192841",
        actor_type="CITIZEN",
        outcome="SUCCESS",
        metadata={
            "username": "rahul.sharma",
            "password": "SuperSecretPassword123!",
            "aadhaar_number": "9988-7766-5544",
            "authorization_header": "Bearer eyJhbGciOi...",
            "subjectReference": "subj_rahul_99"
        }
    )

    json_output = event.to_json()
    parsed = json.loads(json_output)

    assert parsed["metadata"]["username"] == "rahul.sharma"
    assert parsed["metadata"]["subjectReference"] == "subj_rahul_99"
    # Verify sensitive fields are scrubbed
    assert parsed["metadata"]["password"] == "[REDACTED_SENSITIVE_DATA]"
    assert parsed["metadata"]["aadhaar_number"] == "[REDACTED_SENSITIVE_DATA]"
    assert parsed["metadata"]["authorization_header"] == "[REDACTED_SENSITIVE_DATA]"
    assert "SuperSecretPassword123!" not in json_output
    print("    [PASS] Structured logging & automatic PII scrubbing verified")

def test_metrics_and_distributed_tracing():
    print(">>> 2. Testing Metrics & Distributed Tracing...")
    metrics = MetricsCollector()
    tracer = DistributedTracer()

    # Record API latencies
    metrics.record_latency("api_latency_ms", 10.5)
    metrics.record_latency("api_latency_ms", 22.0)
    metrics.record_latency("api_latency_ms", 45.0)
    metrics.increment_counter("api_requests_total", 3)

    percentiles = metrics.calculate_percentiles("api_latency_ms")
    assert percentiles["count"] == 3
    assert percentiles["p50"] > 0
    assert metrics.get_counter("api_requests_total") == 3

    # Start distributed trace with child spans
    root_span = tracer.start_trace(root_name="HTTP POST /v1/verifications", request_id="req_test_001")
    span_consent = tracer.start_child_span(root_span, name="ConsentEngine.evaluate")
    span_consent.finish(status="OK")

    span_provider = tracer.start_child_span(root_span, name="ProviderGateway.execute")
    span_provider.finish(status="OK")

    root_span.finish(status="OK")

    tree = tracer.get_trace_tree(root_span.trace_id)
    assert len(tree) == 3
    assert tree[0]["name"] == "HTTP POST /v1/verifications"
    assert tree[1]["parentSpanId"] == root_span.span_id
    assert tree[2]["parentSpanId"] == root_span.span_id
    print("    [PASS] Metrics collection & distributed tracing verified")

def test_health_probes_and_operations_dashboard():
    print(">>> 3. Testing Health Probes & Operations Dashboard...")
    probes = HealthProbeManager()
    metrics = MetricsCollector()
    dlq = DeadLetterQueueService()
    alert_mgr = AlertAndIncidentManager()

    dashboard = OperationsDashboardService(probes, metrics, dlq, alert_mgr)

    # 1. Liveness check -> always ALIVE
    live = probes.check_liveness()
    assert live["status"] == "alive"

    # 2. Readiness check -> READY
    ready = probes.check_readiness()
    assert ready["status"] == "ready"
    assert ready["dependencies"]["database"] == "healthy"

    # 3. Simulate degraded database dependency
    probes.register_check("database", lambda: False)
    ready_degraded = probes.check_readiness()
    assert ready_degraded["status"] == "degraded"
    assert ready_degraded["dependencies"]["database"] == "unhealthy"

    # 4. Operations snapshot
    snap = dashboard.get_operations_snapshot()
    assert snap["status"] == "degraded"
    assert "slaMetrics" in snap
    assert "queues" in snap
    print("    [PASS] Health probes & operations snapshot verified")

def test_alerting_and_incident_lifecycle():
    print(">>> 4. Testing Alerting & Incident Lifecycle...")
    alert_mgr = AlertAndIncidentManager()

    # Fire P0 Critical Alert
    alert = alert_mgr.fire_alert(
        severity="P0",
        title="Global Cryptographic Signature Failure",
        description="Proof verification rejecting valid proofs due to key store timeout",
        subsystem="proof_engine"
    )
    assert alert.status == "FIRING"

    # Verify incident was automatically opened
    open_incidents = alert_mgr.list_open_incidents()
    assert len(open_incidents) == 1
    inc = open_incidents[0]
    assert inc.severity == "P0"
    assert inc.status == "OPEN"

    # Incident lifecycle progression
    inc.transition_status("INVESTIGATING", note="On-call engineer reviewing KMS latency")
    assert inc.status == "INVESTIGATING"

    inc.transition_status("MITIGATING", note="Key cache warm-up triggered")
    assert inc.status == "MITIGATING"

    inc.transition_status("RESOLVED", note="Key cache healthy, verification latency back to normal")
    assert inc.status == "RESOLVED"
    assert inc.resolved_at is not None
    assert len(alert_mgr.list_open_incidents()) == 0
    print("    [PASS] Alerting & incident lifecycle progression verified")

def test_dead_letter_queue_and_backup_verifier():
    print(">>> 5. Testing DLQ Job Recovery & Backup Verification...")
    dlq = DeadLetterQueueService(max_retries=3)

    # 1. Failure below retry limit -> NOT quarantined
    res1 = dlq.handle_job_failure("WEBHOOK", {"url": "https://foo.com"}, "504 Gateway Timeout", attempt=1)
    assert res1 is None

    # 2. Failure at attempt 3 -> Quarantined to DLQ
    quarantined = dlq.handle_job_failure(
        job_type="WEBHOOK",
        payload={"url": "https://foo.com", "event": "proof.issued"},
        error_message="504 Gateway Timeout",
        attempt=3,
        idempotency_key="idem_webhook_test_01"
    )
    assert quarantined is not None
    assert quarantined.status == "QUARANTINED"
    assert len(dlq.list_quarantined_jobs()) == 1

    # 3. Operator Replay of DLQ job
    ok, err, replay_res = dlq.replay_job(quarantined.id)
    assert ok is True
    assert replay_res["status"] == "SUCCESSFULLY_REPROCESSED"
    assert len(dlq.list_quarantined_jobs()) == 0

    # 4. Cryptographic Backup Verification
    snapshot_data = b"DIGIIN_PRODUCTION_DATABASE_ENCRYPTED_SNAPSHOT_DATA_2026_VERSION_1"
    valid_checksum = hashlib.sha256(snapshot_data).hexdigest()

    # Valid backup -> PASS
    b_res = BackupVerifier.verify_snapshot_integrity("bkp_2026_08_23", snapshot_data, valid_checksum)
    assert b_res.valid is True
    assert b_res.is_decryptable is True

    # Tampered backup -> FAIL (CHECKSUM_MISMATCH)
    b_tampered = BackupVerifier.verify_snapshot_integrity("bkp_tampered", snapshot_data + b"_corrupt", valid_checksum)
    assert b_tampered.valid is False
    assert "CHECKSUM_MISMATCH" in b_tampered.error
    print("    [PASS] DLQ quarantine/replay & backup verification verified")

def test_feature_flags_and_canary_rollout():
    print(">>> 6. Testing Feature Flags & Canary Rollouts...")
    ff_mgr = FeatureFlagManager()

    # 50% Canary Rollout
    ff_mgr.set_flag("FF_CANARY_FEATURE", enabled=True, rollout_percentage=50)
    
    # Deterministic behavior per user
    user1_status = ff_mgr.is_feature_enabled("FF_CANARY_FEATURE", user_id="user_alpha")
    user1_status_again = ff_mgr.is_feature_enabled("FF_CANARY_FEATURE", user_id="user_alpha")
    assert user1_status == user1_status_again

    # Maintenance mode disables feature completely
    ff_mgr.set_flag("FF_CANARY_FEATURE", enabled=True, rollout_percentage=100, maintenance_mode=True)
    assert ff_mgr.is_feature_enabled("FF_CANARY_FEATURE", user_id="user_alpha") is False
    print("    [PASS] Feature flags & canary rollout verified")

def run_all_observability_tests():
    print("=" * 80)
    print("DIGIIN PHASE 21 OBSERVABILITY, RELIABILITY & OPERATIONS TEST MATRIX")
    print("=" * 80)
    test_structured_logging_and_pii_scrubbing()
    test_metrics_and_distributed_tracing()
    test_health_probes_and_operations_dashboard()
    test_alerting_and_incident_lifecycle()
    test_dead_letter_queue_and_backup_verifier()
    test_feature_flags_and_canary_rollout()
    print("=" * 80)
    print("SUCCESS: ALL 6 OBSERVABILITY & RELIABILITY TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_observability_tests()
