"""
DigiIn Service Verification — Citizen Request Inbox & Consent Center
Manages citizen view of pending verification requests (/dashboard/requests) and handles explicit approval ([Allow & Verify]) or denial ([Deny]).
"""

from __future__ import annotations

from .verification_request_model import RequestLifecycleStatus, ServiceVerificationRequest


class CitizenRequestInbox:
    def __init__(self):
        self._requests_by_subject: dict[str, list[ServiceVerificationRequest]] = {}

    def register_request(self, request: ServiceVerificationRequest):
        subj = request.subject_account_id
        if subj not in self._requests_by_subject:
            self._requests_by_subject[subj] = []
        self._requests_by_subject[subj].append(request)
        request.transition_to(RequestLifecycleStatus.DELIVERED, actor="DIGIIN_INBOX")

    def list_requests_for_subject(self, subject_account_id: str, status_filter: str | None = None) -> list[ServiceVerificationRequest]:
        reqs = self._requests_by_subject.get(subject_account_id, [])
        if status_filter:
            reqs = [r for r in reqs if r.status == status_filter]
        return reqs

    def view_request_detail(self, request_id: str, subject_account_id: str) -> ServiceVerificationRequest | None:
        reqs = self._requests_by_subject.get(subject_account_id, [])
        for r in reqs:
            if r.request_id == request_id:
                if r.status == RequestLifecycleStatus.DELIVERED:
                    r.transition_to(RequestLifecycleStatus.VIEWED, actor="CITIZEN")
                return r
        return None

    def deny_request(self, request_id: str, subject_account_id: str, reason: str = "CITIZEN_DECLINED") -> bool:
        req = self.view_request_detail(request_id, subject_account_id)
        if not req or req.status != RequestLifecycleStatus.VIEWED:
            return False
        ok, _ = req.transition_to(RequestLifecycleStatus.DENIED, actor="CITIZEN", reason=reason)
        return ok
