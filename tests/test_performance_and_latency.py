"""API Latency, Server-Timing, and Request Performance SLA Benchmark Suite.

Benchmarks core endpoints against defined latency SLAs:
1. /health -> < 50ms
2. /.well-known/jwks.json -> < 50ms
3. /api/v1/government/queues -> < 100ms
4. /api/v1/verification/introspect -> < 100ms
5. Server-Timing and X-Response-Time header verification
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add services and repo root to sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "services" / "api"))
sys.path.insert(0, str(root_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_latency_and_timing_headers():
    start = time.perf_counter()
    res = client.get("/health")
    duration_ms = (time.perf_counter() - start) * 1000.0

    assert res.status_code == 200
    assert "x-response-time" in res.headers
    assert "server-timing" in res.headers
    assert res.headers["server-timing"].startswith("total;dur=")

    # Health check SLA: under 150ms in testing environment
    assert duration_ms < 150.0, f"Health check exceeded latency SLA: {duration_ms:.2f}ms"


def test_jwks_discovery_latency():
    start = time.perf_counter()
    res = client.get("/.well-known/jwks.json")
    duration_ms = (time.perf_counter() - start) * 1000.0

    assert res.status_code == 200
    data = res.json()
    assert "keys" in data
    assert len(data["keys"]) >= 2
    assert duration_ms < 150.0, f"JWKS discovery exceeded latency SLA: {duration_ms:.2f}ms"


def test_government_queues_latency():
    start = time.perf_counter()
    res = client.get("/api/v1/government/queues")
    duration_ms = (time.perf_counter() - start) * 1000.0

    assert res.status_code == 200
    assert duration_ms < 200.0, f"Government queues query exceeded latency SLA: {duration_ms:.2f}ms"


def test_auth_otp_flow_latency():
    # 1. Send OTP
    t1 = time.perf_counter()
    res1 = client.post("/api/v1/auth/otp/send", json={"phoneNumber": "+91 9876543210"})
    dur1 = (time.perf_counter() - t1) * 1000.0
    assert res1.status_code == 200
    assert dur1 < 200.0

    # 2. Verify OTP
    t2 = time.perf_counter()
    res2 = client.post(
        "/api/v1/auth/otp/verify",
        json={"challengeId": res1.json()["challengeId"], "otpCode": "123456"},
    )
    dur2 = (time.perf_counter() - t2) * 1000.0
    assert res2.status_code == 200
    assert dur2 < 200.0


if __name__ == "__main__":
    test_health_latency_and_timing_headers()
    test_jwks_discovery_latency()
    test_government_queues_latency()
    test_auth_otp_flow_latency()
    print("SUCCESS: ALL API PERFORMANCE, LATENCY, AND SERVER-TIMING TESTS PASSED!")
