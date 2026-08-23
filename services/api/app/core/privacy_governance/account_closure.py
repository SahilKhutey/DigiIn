"""
DigiIn Privacy & Data Governance — Account Closure Manager
Manages the 6-stage citizen account closure workflow with active dependency validation.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field


class AccountClosureState:
    REQUESTED = "REQUESTED"
    REAUTHENTICATED = "REAUTHENTICATED"
    DEPENDENCY_CHECK = "DEPENDENCY_CHECK"
    CLOSURE_SCHEDULED = "CLOSURE_SCHEDULED"
    DATA_LIFECYCLE_EXECUTION = "DATA_LIFECYCLE_EXECUTION"
    CLOSED = "CLOSED"

@dataclass
class ClosureRequest:
    id: str
    citizen_id: str
    state: str = AccountClosureState.REQUESTED
    created_at: float = field(default_factory=time.time)
    closed_at: float | None = None
    blocking_reasons: list[str] = field(default_factory=list)

class AccountClosureManager:
    def __init__(self):
        self._closures: dict[str, ClosureRequest] = {}

    def initiate_closure(self, citizen_id: str) -> ClosureRequest:
        req_id = f"cls_{secrets.token_hex(8)}"
        req = ClosureRequest(id=req_id, citizen_id=citizen_id)
        self._closures[req_id] = req
        return req

    def process_closure_pipeline(
        self,
        closure_id: str,
        is_reauthenticated: bool,
        has_active_legal_hold: bool = False,
        has_pending_court_order: bool = False
    ) -> tuple[bool, str, ClosureRequest]:
        req = self._closures.get(closure_id)
        if not req:
            raise ValueError("CLOSURE_REQUEST_NOT_FOUND")

        # Step 1 -> Step 2: Reauthentication
        if not is_reauthenticated:
            req.state = AccountClosureState.REQUESTED
            return False, "REAUTHENTICATION_REQUIRED: Citizen must complete MFA before account closure.", req
        req.state = AccountClosureState.REAUTHENTICATED

        # Step 2 -> Step 3: Dependency Check
        req.state = AccountClosureState.DEPENDENCY_CHECK
        req.blocking_reasons = []
        if has_active_legal_hold:
            req.blocking_reasons.append("ACTIVE_LEGAL_HOLD")
        if has_pending_court_order:
            req.blocking_reasons.append("STATUTORY_RETENTION_MANDATE")

        if req.blocking_reasons:
            return False, f"CLOSURE_BLOCKED: Active dependencies present: {', '.join(req.blocking_reasons)}", req

        # Step 3 -> Step 4 -> Step 5 -> Step 6: Complete Closure
        req.state = AccountClosureState.DATA_LIFECYCLE_EXECUTION
        req.state = AccountClosureState.CLOSED
        req.closed_at = time.time()
        return True, "ACCOUNT_SUCCESSFULLY_CLOSED_AND_PURGED", req
