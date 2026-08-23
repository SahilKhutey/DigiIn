"""
DigiIn Observability Subsystem — Distributed Tracing Context
Manages trace propagation across API Gateway, Verification Engine, Provider Adapters, and Proof Issuance.
"""

from __future__ import annotations

import secrets
import time
from typing import Any


class Span:
    def __init__(self, trace_id: str, span_id: str, name: str, parent_span_id: str | None = None):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.name = name
        self.start_time = time.time()
        self.end_time: float | None = None
        self.tags: dict[str, Any] = {}
        self.status = "ACTIVE"

    def set_tag(self, key: str, value: Any):
        self.tags[key] = value

    def finish(self, status: str = "OK"):
        self.end_time = time.time()
        self.status = status

    @property
    def duration_ms(self) -> float:
        end = self.end_time or time.time()
        return round((end - self.start_time) * 1000.0, 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "traceId": self.trace_id,
            "spanId": self.span_id,
            "parentSpanId": self.parent_span_id,
            "name": self.name,
            "durationMs": self.duration_ms,
            "status": self.status,
            "tags": self.tags,
        }

class DistributedTracer:
    def __init__(self):
        self.spans: list[Span] = []

    def start_trace(self, root_name: str, request_id: str | None = None) -> Span:
        trace_id = f"trc_{secrets.token_hex(12)}"
        span_id = f"spn_{secrets.token_hex(8)}"
        span = Span(trace_id=trace_id, span_id=span_id, name=root_name)
        if request_id:
            span.set_tag("requestId", request_id)
        self.spans.append(span)
        return span

    def start_child_span(self, parent_span: Span, name: str) -> Span:
        span_id = f"spn_{secrets.token_hex(8)}"
        span = Span(
            trace_id=parent_span.trace_id,
            span_id=span_id,
            parent_span_id=parent_span.span_id,
            name=name
        )
        self.spans.append(span)
        return span

    def get_trace_tree(self, trace_id: str) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self.spans if s.trace_id == trace_id]
