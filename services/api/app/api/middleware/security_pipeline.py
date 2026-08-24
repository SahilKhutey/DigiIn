"""Phase 8.9 — Security Middleware Pipeline.

Consistent security pipeline applied to every API request:

  Request
    ↓ X-Request-ID injection
    ↓ Security headers enforcement
    ↓ Oversized payload check
    ↓ Path traversal / injection pattern detection
    ↓ Structured request logging (no PII)
    ↓ [Business logic]
    ↓ Response security headers
    ↓ Response timing header (for SLA monitoring)

Security headers enforced:
  Content-Security-Policy
  Strict-Transport-Security
  X-Content-Type-Options
  X-Frame-Options
  Referrer-Policy
  Permissions-Policy
  X-Request-ID (injected)
  X-Response-Time (injected)
"""

from __future__ import annotations

import logging
import re
import time
import uuid
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("digiin.security")


# ---------------------------------------------------------------------------
# Security headers
# ---------------------------------------------------------------------------

SECURITY_HEADERS: dict[str, str] = {
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "font-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'none';"
    ),
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": (
        "camera=(), microphone=(), geolocation=(), payment=(), "
        "usb=(), interest-cohort=()"
    ),
    "X-XSS-Protection": "1; mode=block",
    "Cache-Control": "no-store, no-cache, must-revalidate",
}

# ---------------------------------------------------------------------------
# Threat detection patterns
# ---------------------------------------------------------------------------

_PATH_TRAVERSAL = re.compile(r"\.\.[/\\]")
_SQL_INJECTION = re.compile(
    r"(union\s+select|drop\s+table|insert\s+into|delete\s+from|exec\s*\(|xp_cmdshell)",
    re.IGNORECASE,
)
_SCRIPT_INJECTION = re.compile(r"<script[\s>]|javascript:|vbscript:", re.IGNORECASE)

# Maximum allowed payload size: 15 MB (documents up to 10 MB + JSON overhead)
MAX_PAYLOAD_BYTES = 15 * 1024 * 1024


def _detect_threats(path: str, query: str) -> list[str]:
    """Return list of threat names detected in request path+query."""
    threats = []
    target = path + "?" + query
    if _PATH_TRAVERSAL.search(target):
        threats.append("path_traversal")
    if _SQL_INJECTION.search(target):
        threats.append("sql_injection")
    if _SCRIPT_INJECTION.search(target):
        threats.append("script_injection")
    return threats


# ---------------------------------------------------------------------------
# Security Pipeline Middleware
# ---------------------------------------------------------------------------


class SecurityPipelineMiddleware(BaseHTTPMiddleware):
    """
    Unified security middleware applied to every API request.

    Injects X-Request-ID, enforces security headers, detects injection
    patterns, checks oversized payloads, and emits structured audit logs.
    """

    def __init__(self, app: Any, max_payload_bytes: int = MAX_PAYLOAD_BYTES) -> None:
        super().__init__(app)
        self._max_payload = max_payload_bytes

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        start_time = time.monotonic()
        request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"

        # Store request_id in request state for downstream access
        request.state.request_id = request_id

        # Threat detection on path and query string
        threats = _detect_threats(
            str(request.url.path),
            str(request.url.query),
        )
        if threats:
            logger.warning(
                "Threat detected — request_id=%s path=%s threats=%s ip=%s",
                request_id,
                request.url.path,
                threats,
                request.client.host if request.client else "unknown",
            )
            from starlette.responses import JSONResponse
            return JSONResponse(
                status_code=400,
                content={"detail": "Request contains disallowed patterns"},
                headers={
                    "X-Request-ID": request_id,
                    **SECURITY_HEADERS,
                },
            )

        # Content-Length check
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self._max_payload:
            logger.warning(
                "Oversized payload — request_id=%s size=%s limit=%s",
                request_id, content_length, self._max_payload,
            )
            from starlette.responses import JSONResponse
            return JSONResponse(
                status_code=413,
                content={"detail": "Payload too large"},
                headers={"X-Request-ID": request_id},
            )

        # Structured request log (no PII)
        logger.info(
            "request request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        response = await call_next(request)

        # Inject security headers and request tracking
        elapsed_ms = int((time.monotonic() - start_time) * 1000)
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{elapsed_ms}ms"

        # Structured response log
        logger.info(
            "response request_id=%s status=%s elapsed_ms=%s",
            request_id,
            response.status_code,
            elapsed_ms,
        )

        return response


# ---------------------------------------------------------------------------
# Middleware init helper for main.py
# ---------------------------------------------------------------------------

def add_security_pipeline(app: Any, max_payload_bytes: int = MAX_PAYLOAD_BYTES) -> None:
    """Attach SecurityPipelineMiddleware to a FastAPI app."""
    app.add_middleware(SecurityPipelineMiddleware, max_payload_bytes=max_payload_bytes)
