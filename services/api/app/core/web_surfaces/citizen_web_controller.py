"""
DigiIn Web Surfaces — Citizen Web App Controller
Manages citizen dashboard aggregation, credential management, request inbox tabs, consent center, and activity timeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CitizenDashboardSummary:
    pending_requests_count: int
    verified_credentials_count: int
    pending_credentials_count: int
    active_consents_count: int
    recent_activity_count: int

class CitizenWebController:
    def __init__(self, request_inbox: Any, activity_mgr: Any = None):
        self.request_inbox = request_inbox
        self.activity_mgr = activity_mgr

    def get_dashboard_summary(self, subject_account_id: str, credentials_list: list[Any]) -> CitizenDashboardSummary:
        reqs = self.request_inbox.list_requests_for_subject(subject_account_id) if hasattr(self.request_inbox, "list_requests_for_subject") else []
        pending_reqs = len([r for r in reqs if getattr(r, "status", "") in ("DELIVERED", "VIEWED", "PENDING")])
        verified_creds = len([c for c in credentials_list if getattr(c, "status", "") in ("ACTIVE", "VERIFIED")])
        pending_creds = len([c for c in credentials_list if getattr(c, "status", "") == "PENDING"])
        activities = self.activity_mgr.get_user_activity(subject_account_id) if self.activity_mgr else []

        return CitizenDashboardSummary(
            pending_requests_count=pending_reqs,
            verified_credentials_count=verified_creds,
            pending_credentials_count=pending_creds,
            active_consents_count=1,
            recent_activity_count=len(activities)
        )

    def filter_requests_by_tab(self, subject_account_id: str, tab: str = "PENDING") -> list[Any]:
        reqs = self.request_inbox.list_requests_for_subject(subject_account_id) if hasattr(self.request_inbox, "list_requests_for_subject") else []
        if tab == "PENDING":
            return [r for r in reqs if getattr(r, "status", "") in ("DELIVERED", "VIEWED", "PENDING")]
        elif tab == "COMPLETED":
            return [r for r in reqs if getattr(r, "status", "") == "COMPLETED"]
        elif tab == "DENIED":
            return [r for r in reqs if getattr(r, "status", "") == "DENIED"]
        elif tab == "EXPIRED":
            return [r for r in reqs if getattr(r, "status", "") == "EXPIRED"]
        return reqs
