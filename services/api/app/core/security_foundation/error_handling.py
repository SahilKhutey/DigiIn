"""
DigiIn Core Security Subsystem — Standardized Error Model
Emits consistent machine-readable error responses without leaking internal stack traces.
"""

from typing import Any


class DigiInErrorCode:
    AUTH_REQUIRED = "AUTH_REQUIRED"
    AUTH_INVALID = "AUTH_INVALID"
    FORBIDDEN = "FORBIDDEN"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    CONSENT_REQUIRED = "CONSENT_REQUIRED"
    CONSENT_EXPIRED = "CONSENT_EXPIRED"
    DOCUMENT_INVALID = "DOCUMENT_INVALID"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"

class DigiInSecurityException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, request_id: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.request_id = request_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "requestId": self.request_id or "req_unknown"
            }
        }

def format_error_response(code: str, message: str, request_id: str, status_code: int = 400) -> dict[str, Any]:
    """Helper to format standardized public error body."""
    return {
        "error": {
            "code": code,
            "message": message,
            "requestId": request_id
        }
    }
