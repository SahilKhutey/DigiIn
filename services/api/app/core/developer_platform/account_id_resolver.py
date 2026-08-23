"""
DigiIn Developer Platform — Account ID Resolution & Anti-Enumeration Guard
Resolves non-guessable, non-sequential DigiIn Account IDs (e.g. DGI-7F8K-99MX, DGI-SBX-001) without leaking subject PII.
"""

from __future__ import annotations

from typing import Any


class AccountIdResolver:
    def __init__(self):
        # Maps opaque account IDs to internal subject references (in production backed by encrypted subject mapping)
        self._accounts: dict[str, dict[str, Any]] = {
            "DGI-SBX-001": {"subject_ref": "subj_synthetic_rahul_01", "is_sandbox": True, "active": True},
            "DGI-SBX-002": {"subject_ref": "subj_synthetic_priya_02", "is_sandbox": True, "active": True},
            "DGI-7F8K-99MX": {"subject_ref": "subj_citizen_prod_8812", "is_sandbox": False, "active": True},
        }
        self._failed_lookups: dict[str, int] = {}

    def resolve_account_id(self, account_id: str, client_ip: str = "127.0.0.1") -> tuple[bool, str | None, str | None]:
        """
        Resolve DigiIn Account ID to minimal subject reference.
        Enforces anti-enumeration rate limiting on failed lookups.
        """
        # Anti-enumeration rate check: if client has >10 consecutive invalid lookups, throttle
        fails = self._failed_lookups.get(client_ip, 0)
        if fails >= 10:
            return False, "RATE_LIMITED: Too many consecutive invalid Account ID lookups. Throttled for abuse prevention.", None

        entry = self._accounts.get(account_id)
        if not entry or not entry.get("active"):
            self._failed_lookups[client_ip] = fails + 1
            # Return opaque uniform error to prevent timing/oracle enumeration
            return False, "SUBJECT_NOT_FOUND: The requested DigiIn Account ID does not exist or is inactive.", None

        # Reset failed count on successful match
        self._failed_lookups[client_ip] = 0
        return True, None, entry["subject_ref"]

    def register_account(self, account_id: str, subject_ref: str, is_sandbox: bool = False):
        self._accounts[account_id] = {"subject_ref": subject_ref, "is_sandbox": is_sandbox, "active": True}
