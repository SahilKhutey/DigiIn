"""
DigiIn Automated Performance, Scalability & High-Load Test Suite (Phase 24)
Validates Performance Context, Safe Caching, Cursor Pagination, Queue Governor, Provider Circuit Breaker, Distributed Rate Limiter, Idempotency, and Chunked Uploads.
"""

import sys
import os
import time
import hashlib

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.performance import (
    DependencyTimer,
    SafeTieredCache,
    CursorPaginator,
    ResponseProjector,
    QueueScalingGovernor,
    ProviderCircuitBreaker,
    CircuitState,
    ExponentialBackoffRetry,
    DistributedRateLimiter,
    IdempotencyEngine,
    ChunkedUploadManager,
    PerformanceBudgetEvaluator,
)

def test_performance_context_and_budgets():
    print(">>> 1. Testing Performance Context & Budget Evaluation...")
    ctx = DependencyTimer.create_context(operation="POST /v1/verifications", actor_type="ORGANIZATION", org_id="org_delhi_univ")

    # Simulate sub-stages
    ctx.start_stage("auth")
    time.sleep(0.01)
    ctx.end_stage("auth")

    ctx.start_stage("policy")
    time.sleep(0.005)
    ctx.end_stage("policy")

    ctx.start_stage("database")
    time.sleep(0.015)
    ctx.end_stage("database")

    final = ctx.finalize()
    assert final["requestId"] is not None
    assert final["operation"] == "POST /v1/verifications"
    assert "auth" in final["timings"]
    assert "database" in final["timings"]

    # Evaluate budgets
    evaluator = PerformanceBudgetEvaluator()
    passed, budget_res = evaluator.evaluate_metric("api_overall", actual_p95_ms=320.0, actual_p99_ms=650.0)
    assert passed is True
    assert budget_res["p95"]["passed"] is True
    print("    [PASS] Performance context & SLO budget evaluation verified")

def test_safe_caching_and_privacy_guards():
    print(">>> 2. Testing Safe Reference Caching & Privacy Guards...")
    cache = SafeTieredCache(default_ttl_seconds=60)

    # 1. Cache safe public reference data -> ALLOW
    cache.set("provider:meta:cbse-01", {"name": "CBSE Board", "tier": "SOVEREIGN"})
    val = cache.get("provider:meta:cbse-01")
    assert val["name"] == "CBSE Board"

    # 2. Invalidate cache
    assert cache.invalidate("provider:meta:cbse-01") is True
    assert cache.get("provider:meta:cbse-01") is None

    # 3. Attempt to cache raw citizen Aadhaar / Password -> PRIVACY_CACHE_VIOLATION
    try:
        cache.set("user:aadhaar:9988-7766-5544", {"citizen": "Rahul"})
        assert False, "SafeTieredCache allowed caching sensitive Aadhaar PII!"
    except ValueError as ex:
        assert "PRIVACY_CACHE_VIOLATION" in str(ex)
    print("    [PASS] Safe reference caching & privacy guards verified")

def test_cursor_pagination_and_projection():
    print(">>> 3. Testing Cursor Pagination & Response Projection...")
    records = [
        {"id": f"rec_{i:02d}", "status": "VERIFIED", "created_at": 1700000000 + i, "secret_internal": "foo"}
        for i in range(15)
    ]

    # Page 1 (limit 5)
    p1 = CursorPaginator.paginate_records(records, limit=5)
    assert len(p1["items"]) == 5
    assert p1["hasMore"] is True
    assert p1["nextCursor"] is not None

    # Page 2 using cursor
    p2 = CursorPaginator.paginate_records(records, limit=5, cursor=p1["nextCursor"])
    assert len(p2["items"]) == 5
    assert p2["items"][0]["id"] == "rec_05"

    # Projection (exclude secret_internal)
    projected = ResponseProjector.project_fields(p2["items"][0], ["id", "status", "created_at"])
    assert "id" in projected
    assert "secret_internal" not in projected
    print("    [PASS] Cursor pagination & field projection verified")

def test_queue_scaling_and_provider_circuit_breaker():
    print(">>> 4. Testing Queue Scaling & Provider Circuit Breaker...")
    # 1. Queue Governor Concurrency Scaling
    governor = QueueScalingGovernor(base_concurrency=5, max_concurrency=50, high_watermark_depth=500)
    
    governor.update_queue_depth("verification", 50)
    assert governor.calculate_worker_concurrency("verification") == 5  # Baseline

    governor.update_queue_depth("verification", 300)
    assert governor.calculate_worker_concurrency("verification") > 20  # Scaled up

    governor.update_queue_depth("verification", 1500)
    assert governor.is_backpressure_active("verification") is True

    # 2. Provider Circuit Breaker
    cb = ProviderCircuitBreaker(provider_id="cbse-live", failure_threshold=3, recovery_timeout_seconds=0.1)
    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() is True

    # 3 consecutive failures -> Trip to OPEN
    cb.record_failure()
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False

    # Wait for recovery timeout -> Transition to HALF_OPEN
    time.sleep(0.15)
    assert cb.can_execute() is True
    assert cb.state == CircuitState.HALF_OPEN

    # Success heals circuit back to CLOSED
    cb.record_success()
    assert cb.state == CircuitState.CLOSED

    # Exponential Backoff with Jitter
    delay = ExponentialBackoffRetry.calculate_delay(attempt=3, base_delay=1.0)
    assert delay > 0.0
    print("    [PASS] Queue scaling governor & provider circuit breaker verified")

def test_distributed_rate_limiting_and_idempotency():
    print(">>> 5. Testing Distributed Rate Limiting & Idempotency Engine...")
    # 1. Rate Limiting Token Bucket
    limiter = DistributedRateLimiter()
    # Capacity 3, refill 1/sec
    ok1, _ = limiter.check_rate_limit("org_burst_test", capacity=3, refill_rate_per_sec=1.0)
    ok2, _ = limiter.check_rate_limit("org_burst_test", capacity=3, refill_rate_per_sec=1.0)
    ok3, _ = limiter.check_rate_limit("org_burst_test", capacity=3, refill_rate_per_sec=1.0)
    ok4, _ = limiter.check_rate_limit("org_burst_test", capacity=3, refill_rate_per_sec=1.0)

    assert ok1 and ok2 and ok3 is True
    assert ok4 is False  # 4th burst request throttled!

    # 2. Idempotency Engine
    idem = IdempotencyEngine()
    idem_key = "idem_key_unique_test_99"
    payload = {"subjectId": "DGI-SBX-001", "type": "DEGREE"}
    response = {"verificationId": "vreq_8819", "status": "VERIFIED"}

    # First request: Miss
    hit1, _ = idem.process_idempotent_request(idem_key, payload)
    assert hit1 is False

    # Store response
    idem.store_response(idem_key, payload, response)

    # Second request with identical payload: Cache Hit!
    hit2, cached_resp = idem.process_idempotent_request(idem_key, payload)
    assert hit2 is True
    assert cached_resp["verificationId"] == "vreq_8819"

    # Conflicting payload with same key -> Conflict Error
    try:
        idem.process_idempotent_request(idem_key, {"subjectId": "DGI-OTHER-ACCOUNT"})
        assert False, "Idempotency engine allowed key reuse with conflicting payload!"
    except ValueError as ex:
        assert "IDEMPOTENCY_KEY_REUSE_PAYLOAD_MISMATCH" in str(ex)
    print("    [PASS] Distributed rate limiting & idempotency deduplication verified")

def test_resumable_chunked_upload():
    print(">>> 6. Testing Resumable Chunked Direct Upload...")
    chunk_mgr = ChunkedUploadManager(chunk_size_bytes=10)
    total_data = b"DIGIIN_CHUNKED_UPLOAD_HIGH_PERFORMANCE_TEST_PAYLOAD_2026"
    expected_sha = hashlib.sha256(total_data).hexdigest()

    # Session initiation
    session = chunk_mgr.initiate_upload_session("doc_chunk_01", len(total_data))
    assert session.expected_chunks == 6  # 57 bytes / 10 = 6 chunks

    # Upload chunks in chunks of 10 bytes
    for i in range(session.expected_chunks):
        chunk_data = total_data[i * 10 : (i + 1) * 10]
        completed, msg, s = chunk_mgr.upload_chunk(session.session_id, i, chunk_data)

    assert completed is True
    assert s.assembled_sha256 == expected_sha
    print("    [PASS] Resumable chunked upload & SHA-256 assembly verified")

def run_all_performance_tests():
    print("=" * 80)
    print("DIGIIN PHASE 24 PERFORMANCE, SCALABILITY & HIGH-LOAD TEST MATRIX")
    print("=" * 80)
    test_performance_context_and_budgets()
    test_safe_caching_and_privacy_guards()
    test_cursor_pagination_and_projection()
    test_queue_scaling_and_provider_circuit_breaker()
    test_distributed_rate_limiting_and_idempotency()
    test_resumable_chunked_upload()
    print("=" * 80)
    print("SUCCESS: ALL 6 PERFORMANCE, SCALABILITY & HIGH-LOAD TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_performance_tests()
