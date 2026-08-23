"""
DigiIn Working Product — User-Friendly Error Shielding
Masks raw internal exceptions and SQL/stack traces into clear, safe user messages correlated with Request IDs.
"""

from __future__ import annotations

from typing import Any


class DigiInError(Exception):
    def __init__(self, code: str, status_code: int, user_message: str, internal_details: str | None = None):
        super().__init__(user_message)
        self.code = code
        self.status_code = status_code
        self.user_message = user_message
        self.internal_details = internal_details

    def to_safe_dict(self, request_id: str) -> dict[str, Any]:
        return {
            "success": False,
            "requestId": request_id,
            "error": {
                "code": self.code,
                "message": self.user_message
            }
        }

class ErrorSanitizer:
    @staticmethod
    def sanitize_exception(exc: Exception, request_id: str) -> dict[str, Any]:
        if isinstance(exc, DigiInError):
            return exc.to_safe_dict(request_id)

        # Fallback for unexpected raw exceptions (ECONNREFUSED, SQL, etc.)
        return {
            "success": False,
            "requestId": request_id,
            "error": {
                "code": "INTERNAL_SERVICE_ERROR",
                "message": "We couldn't complete the operation. Your information has not been changed. Please try again."
            }
        }
