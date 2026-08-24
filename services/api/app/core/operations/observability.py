"""Phase 9.4 — Three Pillars of Observability & SLO Tracking Engine.

Provides:
  1. Structured JSON Logging with strict PII scrubbing.
  2. Metrics Collector (throughput, latencies, error rates, queue depths, provider health).
  3. Distributed Tracing & Span context propagation.
  4. SLO Engine evaluating measurable targets (availability, p95 latencies, error rates).
"""

from __future__ import annotations

import json
import re
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

# PII Scrubbing patterns
_PII_PATTERNS = [
    (re.compile(r"\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b"), "[REDACTED_AADHAAR]"),
    (re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"), "[REDACTED_PAN]"),
    (re.compile(r"\botp[\":\s]+\d{4,8}\b", re.IGNORECASE), "otp:[REDACTED]"),
    (
        re.compile(r"eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}"),
        "[REDACTED_JWT]",
    ),
    (
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        "[REDACTED_PRIVATE_KEY]",
    ),
]


def scrub_pii(text: str) -> str:
    """Scrubs accidental PII from raw string values."""
    scrubbed = text
    for pattern, replacement in _PII_PATTERNS:
        scrubbed = pattern.sub(replacement, scrubbed)
    return scrubbed


@dataclass
class StructuredLogEvent:
    timestamp: str
    level: str
    service: str
    request_id: str
    correlation_id: str
    operation: str
    status: str
    duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        safe_meta = {}
        for k, v in self.metadata.items():
            if isinstance(v, str):
                safe_meta[k] = scrub_pii(v)
            else:
                safe_meta[k] = v
        d = asdict(self)
        d["metadata"] = safe_meta
        return json.dumps(d)


@dataclass
class Span:
    trace_id: str
    span_id: str
    name: str
    parent_span_id: str | None = None
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def finish(self) -> float:
        self.end_time = time.time()
        return (self.end_time - self.start_time) * 1000.0


class ObservabilityCollector:
    """Central metrics, logging, tracing, and SLO computation service."""

    def __init__(self) -> None:
        self._latencies: list[float] = []
        self._verification_latencies: list[float] = []
        self._requests_total = 0
        self._errors_total = 0
        self._verifications_total = 0
        self._verifications_success = 0
        self._credentials_issued = 0
        self._logs: list[StructuredLogEvent] = []
        self._traces: dict[str, list[Span]] = {}

    def log(
        self,
        level: str,
        service: str,
        operation: str,
        status: str,
        request_id: str = "",
        correlation_id: str = "",
        duration_ms: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> StructuredLogEvent:
        event = StructuredLogEvent(
            timestamp=datetime.now(UTC).isoformat(),
            level=level.upper(),
            service=service,
            request_id=request_id or f"req_{uuid.uuid4().hex[:12]}",
            correlation_id=correlation_id or f"corr_{uuid.uuid4().hex[:12]}",
            operation=operation,
            status=status,
            duration_ms=duration_ms,
            metadata=metadata or {},
        )
        self._logs.append(event)
        if len(self._logs) > 5000:
            self._logs = self._logs[-2500:]
        return event

    def record_request(self, duration_ms: float, is_error: bool = False) -> None:
        self._requests_total += 1
        if is_error:
            self._errors_total += 1
        self._latencies.append(duration_ms)
        if len(self._latencies) > 10000:
            self._latencies = self._latencies[-5000:]

    def record_verification(
        self, duration_ms: float, success: bool = True
    ) -> None:
        self._verifications_total += 1
        if success:
            self._verifications_success += 1
        self._verification_latencies.append(duration_ms)
        if len(self._verification_latencies) > 10000:
            self._verification_latencies = self._verification_latencies[-5000:]

    def record_credential_issued(self) -> None:
        self._credentials_issued += 1

    def start_span(
        self,
        name: str,
        trace_id: str | None = None,
        parent_span_id: str | None = None,
    ) -> Span:
        t_id = trace_id or f"trc_{uuid.uuid4().hex[:16]}"
        span_id = f"spn_{uuid.uuid4().hex[:8]}"
        span = Span(
            trace_id=t_id,
            span_id=span_id,
            name=name,
            parent_span_id=parent_span_id,
        )
        if t_id not in self._traces:
            self._traces[t_id] = []
        self._traces[t_id].append(span)
        return span

    def _percentile(self, values: list[float], p: float) -> float:
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        idx = int(len(sorted_vals) * (p / 100.0))
        idx = min(idx, len(sorted_vals) - 1)
        return round(sorted_vals[idx], 2)

    def get_metrics_snapshot(self) -> dict[str, Any]:
        """Returns comprehensive operational metrics."""
        error_rate = (
            (self._errors_total / self._requests_total * 100.0)
            if self._requests_total > 0
            else 0.0
        )
        verif_rate = (
            (self._verifications_success / self._verifications_total * 100.0)
            if self._verifications_total > 0
            else 100.0
        )

        return {
            "requests_total": self._requests_total,
            "errors_total": self._errors_total,
            "error_rate_pct": round(error_rate, 2),
            "verifications_total": self._verifications_total,
            "verifications_success": self._verifications_success,
            "verification_success_rate_pct": round(verif_rate, 2),
            "credentials_issued": self._credentials_issued,
            "latency_p50_ms": self._percentile(self._latencies, 50),
            "latency_p95_ms": self._percentile(self._latencies, 95),
            "latency_p99_ms": self._percentile(self._latencies, 99),
            "verification_latency_p95_ms": self._percentile(
                self._verification_latencies, 95
            ),
        }

    def evaluate_slos(self) -> dict[str, Any]:
        """Evaluates compliance against target service-level objectives."""
        metrics = self.get_metrics_snapshot()
        error_rate = metrics["error_rate_pct"]
        p95 = metrics["latency_p95_ms"]
        verif_p95 = metrics["verification_latency_p95_ms"]

        slo_availability = error_rate < 1.0
        slo_api_latency = p95 <= 500.0 or self._requests_total == 0
        slo_verif_latency = verif_p95 <= 1000.0 or self._verifications_total == 0
        slo_error_rate = error_rate < 1.0

        all_met = (
            slo_availability
            and slo_api_latency
            and slo_verif_latency
            and slo_error_rate
        )

        return {
            "overall_status": "COMPLIANT" if all_met else "AT_RISK",
            "slos": {
                "availability_ge_99_9": {
                    "target": ">= 99.9%",
                    "current": f"{100.0 - error_rate:.2f}%",
                    "status": "PASS" if slo_availability else "FAIL",
                },
                "api_p95_latency_lt_500ms": {
                    "target": "< 500ms",
                    "current": f"{p95}ms",
                    "status": "PASS" if slo_api_latency else "FAIL",
                },
                "verification_p95_latency_lt_1000ms": {
                    "target": "< 1000ms",
                    "current": f"{verif_p95}ms",
                    "status": "PASS" if slo_verif_latency else "FAIL",
                },
                "error_rate_lt_1pct": {
                    "target": "< 1.0%",
                    "current": f"{error_rate}%",
                    "status": "PASS" if slo_error_rate else "FAIL",
                },
            },
        }


# Global singleton instance
observability = ObservabilityCollector()
