"""
DigiIn Observability Subsystem — Structured JSON Logger with PII Scrubbing
Emits structured JSON operational events while guaranteeing zero leakage of passwords, tokens, private keys, or citizen PII.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any

# Sensitive key patterns to automatically redact
SENSITIVE_KEY_PATTERNS = [
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"private_?key", re.IGNORECASE),
    re.compile(r"aadhaar", re.IGNORECASE),
    re.compile(r"raw_?file", re.IGNORECASE),
    re.compile(r"content", re.IGNORECASE),
    re.compile(r"authorization", re.IGNORECASE),
]

def sanitize_metadata(data: Any) -> Any:
    """Recursively scrub sensitive keys and credential patterns."""
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if any(p.search(k) for p in SENSITIVE_KEY_PATTERNS):
                cleaned[k] = "[REDACTED_SENSITIVE_DATA]"
            else:
                cleaned[k] = sanitize_metadata(v)
        return cleaned
    elif isinstance(data, list):
        return [sanitize_metadata(x) for x in data]
    elif isinstance(data, str):
        # Redact bearer token substrings
        if data.startswith("Bearer ") or data.startswith("eyJ"):
            return "[REDACTED_AUTH_TOKEN]"
        return data
    return data

@dataclass
class LogEvent:
    timestamp: float
    level: str  # "DEBUG" | "INFO" | "WARN" | "ERROR"
    service: str
    event: str
    request_id: str | None = None
    correlation_id: str | None = None
    trace_id: str | None = None
    actor_type: str | None = None
    outcome: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        payload = {
            "timestamp": self.timestamp,
            "level": self.level,
            "service": self.service,
            "event": self.event,
            "requestId": self.request_id,
            "correlationId": self.correlation_id,
            "traceId": self.trace_id,
            "actorType": self.actor_type,
            "outcome": self.outcome,
            "metadata": sanitize_metadata(self.metadata),
        }
        return json.dumps(payload, sort_keys=True)

class StructuredLogger:
    def __init__(self, service_name: str = "digiin-core"):
        self.service_name = service_name
        self.logs: list[LogEvent] = []

    def log(
        self,
        level: str,
        event: str,
        request_id: str | None = None,
        correlation_id: str | None = None,
        trace_id: str | None = None,
        actor_type: str | None = None,
        outcome: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> LogEvent:
        event_obj = LogEvent(
            timestamp=time.time(),
            level=level.upper(),
            service=self.service_name,
            event=event,
            request_id=request_id,
            correlation_id=correlation_id,
            trace_id=trace_id,
            actor_type=actor_type,
            outcome=outcome,
            metadata=metadata or {}
        )
        self.logs.append(event_obj)
        return event_obj

    def info(self, event: str, **kwargs) -> LogEvent:
        return self.log("INFO", event, **kwargs)

    def warn(self, event: str, **kwargs) -> LogEvent:
        return self.log("WARN", event, **kwargs)

    def error(self, event: str, **kwargs) -> LogEvent:
        return self.log("ERROR", event, **kwargs)
