"""
DigiIn Working Product — User Action Router
Maps intent-driven user actions to business workflow handlers.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .auth_context import AuthContext
from .request_pipeline import DigiInRequest, DigiInResponse


class UserActionTypes:
    REGISTER_ACCOUNT = "REGISTER_ACCOUNT"
    LOGIN = "LOGIN"
    UPLOAD_DOCUMENT = "UPLOAD_DOCUMENT"
    REQUEST_VERIFICATION = "REQUEST_VERIFICATION"
    APPROVE_CONSENT = "APPROVE_CONSENT"
    DENY_CONSENT = "DENY_CONSENT"
    REVOKE_CONSENT = "REVOKE_CONSENT"
    PRESENT_CREDENTIAL = "PRESENT_CREDENTIAL"
    VERIFY_CLAIM = "VERIFY_CLAIM"

class UserActionRouter:
    def __init__(self):
        self._handlers: dict[str, Callable[[DigiInRequest[Any], AuthContext], DigiInResponse[Any]]] = {}

    def register_handler(
        self,
        action: str,
        handler: Callable[[DigiInRequest[Any], AuthContext], DigiInResponse[Any]]
    ):
        self._handlers[action] = handler

    def dispatch(
        self,
        request: DigiInRequest[Any],
        auth_context: AuthContext
    ) -> DigiInResponse[Any]:
        handler = self._handlers.get(request.action)
        if not handler:
            return DigiInResponse.fail(
                request_id=request.request_id,
                code="UNSUPPORTED_ACTION",
                message=f"No workflow handler registered for action '{request.action}'"
            )

        return handler(request, auth_context)
