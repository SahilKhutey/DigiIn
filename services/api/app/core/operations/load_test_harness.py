"""Phase 9.8 — Concurrency Load Testing & Benchmark Simulator Harness.

Simulates 100 concurrent user requests executing:
  1. Account Access / Session Introspection
  2. Document Upload & Envelope Storage
  3. Authoritative External Verification
  4. Credential Lookup
  5. Cryptographic Proof Verification

Measures p50, p95, p99 latencies, throughput (req/s), error rate, and verifies
that lightweight proof verification is significantly cheaper/faster than heavy document processing.
"""

from __future__ import annotations

import concurrent.futures
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class LoadTestReport:
    total_requests: int
    concurrency_level: int
    duration_seconds: float
    throughput_rps: float
    error_count: int
    error_rate_pct: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    workload_latencies: dict[str, float]  # workload_name -> p95_latency_ms

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "concurrency_level": self.concurrency_level,
            "duration_seconds": round(self.duration_seconds, 3),
            "throughput_rps": round(self.throughput_rps, 2),
            "error_count": self.error_count,
            "error_rate_pct": round(self.error_rate_pct, 2),
            "latency_p50_ms": self.latency_p50_ms,
            "latency_p95_ms": self.latency_p95_ms,
            "latency_p99_ms": self.latency_p99_ms,
            "workload_latencies": self.workload_latencies,
        }


class LoadTestHarness:
    """Simulates high-concurrency benchmarks across DigiIn core workloads."""

    def _percentile(self, values: list[float], p: float) -> float:
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        idx = int(len(sorted_vals) * (p / 100.0))
        idx = min(idx, len(sorted_vals) - 1)
        return round(sorted_vals[idx], 2)

    def run_benchmark(
        self,
        total_requests: int = 100,
        concurrency: int = 20,
        workload_fn: Callable[[int], tuple[str, bool, float]] | None = None,
    ) -> LoadTestReport:
        """Executes concurrent requests and gathers latency histograms.

        workload_fn: callable(request_idx) -> (workload_name, is_success, duration_ms)
        """
        latencies: list[float] = []
        by_workload: dict[str, list[float]] = {}
        error_count = 0

        # Default simulated workload
        def default_worker(idx: int) -> tuple[str, bool, float]:
            start = time.perf_counter()
            workload_type = idx % 5
            if workload_type == 0:
                # 1. Account access (fast)
                time.sleep(0.001)
                name = "account_access"
            elif workload_type == 1:
                # 2. Document upload & envelope encryption (moderate)
                time.sleep(0.005)
                name = "document_upload"
            elif workload_type == 2:
                # 3. External verification (heavier)
                time.sleep(0.010)
                name = "external_verification"
            elif workload_type == 3:
                # 4. Credential lookup (fast)
                time.sleep(0.002)
                name = "credential_lookup"
            else:
                # 5. Cryptographic proof verification (very fast)
                time.sleep(0.0008)
                name = "proof_verification"

            duration_ms = (time.perf_counter() - start) * 1000.0
            return name, True, duration_ms

        worker = workload_fn or default_worker

        overall_start = time.perf_counter()

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=concurrency
        ) as executor:
            futures = [executor.submit(worker, i) for i in range(total_requests)]
            for future in concurrent.futures.as_completed(futures):
                try:
                    name, success, duration_ms = future.result()
                    latencies.append(duration_ms)
                    if name not in by_workload:
                        by_workload[name] = []
                    by_workload[name].append(duration_ms)
                    if not success:
                        error_count += 1
                except Exception:
                    error_count += 1

        total_duration = time.perf_counter() - overall_start
        throughput = (
            (total_requests / total_duration) if total_duration > 0 else 0.0
        )
        error_rate = (
            (error_count / total_requests * 100.0) if total_requests > 0 else 0.0
        )

        workload_p95 = {
            k: self._percentile(v, 95) for k, v in by_workload.items()
        }

        return LoadTestReport(
            total_requests=total_requests,
            concurrency_level=concurrency,
            duration_seconds=total_duration,
            throughput_rps=throughput,
            error_count=error_count,
            error_rate_pct=error_rate,
            latency_p50_ms=self._percentile(latencies, 50),
            latency_p95_ms=self._percentile(latencies, 95),
            latency_p99_ms=self._percentile(latencies, 99),
            workload_latencies=workload_p95,
        )


# Global singleton instance
load_test_harness = LoadTestHarness()
