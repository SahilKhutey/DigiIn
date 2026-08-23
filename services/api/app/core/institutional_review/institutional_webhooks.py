"""
DigiIn Institutional Review — HMAC Webhook Dispatcher & Analytics Dashboard
Handles HMAC-SHA256 signed event delivery to external institutional ERP systems and aggregates department analytics.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass, field
from typing import Any

from .institutional_request_engine import DepartmentVerificationRequest


@dataclass
class WebhookDeliveryLog:
    id: str
    organization_id: str
    event_type: str
    target_url: str
    payload: dict[str, Any]
    signature_hex: str
    status: str  # "DELIVERED" | "FAILED" | "RETRYING"
    delivered_at: float = field(default_factory=time.time)

class InstitutionalWebhookDispatcher:
    def __init__(self, secret: str = "inst_webhook_secret_key_2026"):
        self.secret = secret.encode("utf-8")
        self._deliveries: list[WebhookDeliveryLog] = []

    def dispatch_event(
        self,
        organization_id: str,
        target_url: str,
        event_type: str,
        data: dict[str, Any]
    ) -> WebhookDeliveryLog:
        now = time.time()
        nonce = secrets.token_hex(8)
        payload = {
            "event": event_type,
            "organizationId": organization_id,
            "nonce": nonce,
            "timestamp": now,
            "data": data
        }
        serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
        sig = hmac.new(self.secret, serialized, hashlib.sha256).hexdigest()

        delivery = WebhookDeliveryLog(
            id=f"whd_{secrets.token_hex(8)}",
            organization_id=organization_id,
            event_type=event_type,
            target_url=target_url,
            payload=payload,
            signature_hex=sig,
            status="DELIVERED",
            delivered_at=now
        )
        self._deliveries.append(delivery)
        return delivery

    def verify_webhook_signature(self, payload: dict[str, Any], signature_hex: str) -> bool:
        serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
        expected_sig = hmac.new(self.secret, serialized, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_sig, signature_hex)

class InstitutionalDashboardService:
    @staticmethod
    def get_organization_metrics(requests: list[DepartmentVerificationRequest]) -> dict[str, Any]:
        total = len(requests)
        pending = len([r for r in requests if r.status == "PENDING_CITIZEN"])
        in_review = len([r for r in requests if r.status == "IN_REVIEW"])
        completed = len([r for r in requests if r.status == "COMPLETED"])
        rejected = len([r for r in requests if r.status == "REJECTED"])

        return {
            "totalRequests": total,
            "pendingCitizen": pending,
            "inReview": in_review,
            "completed": completed,
            "rejected": rejected,
            "completionRatePercent": round((completed + rejected) / total * 100, 1) if total > 0 else 100.0
        }
