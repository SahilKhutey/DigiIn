"""
DigiIn Working Product — Standard Request Architecture & Request Pipeline
Defines standard request/response envelopes, 7-stage lifecycle state machines, and idempotency management.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")

class RequestStatus:
    RECEIVED = "RECEIVED"
    AUTHENTICATING = "AUTHENTICATING"
    AUTHORIZED = "AUTHORIZED"
    VALIDATING = "VALIDATING"
    PROCESSING = "PROCESSING"
    QUEUED = "QUEUED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

@dataclass
class Actor:
    type: str  # "USER" | "INSTITUTION" | "SYSTEM"
    id: str

@dataclass
class DigiInRequest(Generic[T]):
    request_id: str
    actor: Actor
    action: str
    payload: T
    context: dict[str, Any] = field(default_factory=dict)
    idempotency_key: str | None = None
    timestamp: float = field(default_factory=time.time)
    status: str = RequestStatus.RECEIVED

    @staticmethod
    def create(actor_type: str, actor_id: str, action: str, payload: T, idempotency_key: str | None = None, context: dict[str, Any] | None = None) -> DigiInRequest[T]:
        rid = f"req_{secrets.token_hex(8)}"
        return DigiInRequest(
            request_id=rid,
            actor=Actor(type=actor_type, id=actor_id),
            action=action,
            payload=payload,
            context=context or {},
            idempotency_key=idempotency_key
        )

@dataclass
class DigiInResponse(Generic[T]):
    success: bool
    request_id: str
    data: T | None = None
    error: dict[str, Any] | None = None
    meta: dict[str, Any] = field(default_factory=lambda: {
        "timestamp": time.time(),
        "version": "1.0.0"
    })

    @staticmethod
    def ok(request_id: str, data: T) -> DigiInResponse[T]:
        return DigiInResponse(success=True, request_id=request_id, data=data)

    @staticmethod
    def fail(request_id: str, code: str, message: str, details: Any | None = None) -> DigiInResponse[Any]:
        return DigiInResponse(
            success=False,
            request_id=request_id,
            error={"code": code, "message": message, "details": details}
        )

class IdempotencyManager:
    def __init__(self):
        self._cache: dict[str, DigiInResponse[Any]] = {}

    def check_and_get(self, key: str) -> DigiInResponse[Any] | None:
        return self._cache.get(key)

    def record_response(self, key: str, response: DigiInResponse[Any]):
        self._cache[key] = response
