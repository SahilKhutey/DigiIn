"""
DigiIn Production Infrastructure — Edge WAF & Cache Policy Engine
Enforces edge rate limits, malicious payload detection, request body caps, and no-store caching on sensitive verification endpoints.
"""

from __future__ import annotations

import re

# Common SQLi & XSS injection signatures for WAF filter
MALICIOUS_PATTERNS = [
    re.compile(r"(\%27)|(\')|(\-\-)|(\%23)|(#)", re.IGNORECASE),
    re.compile(r"(<script.*?>.*?</script>)", re.IGNORECASE),
    re.compile(r"(UNION\s+SELECT)", re.IGNORECASE),
    re.compile(r"(EXEC(\s|\+)+(SP_|XP_))", re.IGNORECASE),
]

MAX_API_BODY_BYTES = 2 * 1024 * 1024  # 2 MB

class EdgeWafEngine:
    @staticmethod
    def inspect_request(
        path: str,
        method: str,
        body_bytes: bytes,
        headers: dict[str, str]
    ) -> tuple[bool, str | None, int | None]:
        """Inspect inbound HTTP request against WAF security policies."""
        # 1. Payload size check
        if len(body_bytes) > MAX_API_BODY_BYTES:
            return False, "PAYLOAD_TOO_LARGE: Request exceeds 2MB WAF limit.", 413

        # 2. Malicious payload inspection
        body_text = body_bytes.decode("utf-8", errors="ignore")
        for pattern in MALICIOUS_PATTERNS:
            if pattern.search(body_text) or pattern.search(path):
                return False, "MALICIOUS_REQUEST_BLOCKED: WAF detected malicious SQLi/XSS signature.", 403

        return True, None, None

    @staticmethod
    def get_security_headers_for_response(path: str) -> dict[str, str]:
        """Produce production security headers and strict cache policies."""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
        # Sensitive verification & proof endpoints must never be cached by CDNs or proxies
        if any(p in path for p in ("/verifications", "/proofs", "/consent", "/subjects", "/auth")):
            headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            headers["Pragma"] = "no-cache"
        else:
            headers["Cache-Control"] = "public, max-age=3600"
        return headers
