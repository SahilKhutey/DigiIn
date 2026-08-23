"""
DigiIn Service Verification — Short-Lived QR Verification & Service Dashboard
Handles short-lived QR verification requests and computes operational dashboard metrics for integrated services (/service/dashboard).
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass
from typing import Any

from .verification_request_model import RequestLifecycleStatus, ServiceVerificationRequest


@dataclass
class QRServiceRequest:
    qr_request_id: str
    service_id: str
    service_name: str
    purpose: str
    requested_claims: list[str]
    nonce: str
    expires_at: float
    signature: str

class QRServiceVerifier:
    @staticmethod
    def generate_qr_request(
        service_id: str,
        service_name: str,
        purpose: str,
        requested_claims: list[str],
        valid_seconds: int = 300
    ) -> tuple[QRServiceRequest, str]:
        qrid = f"qreq_{secrets.token_hex(8)}"
        nonce = secrets.token_hex(12)
        exp = time.time() + valid_seconds
        sig = secrets.token_hex(32)

        req = QRServiceRequest(
            qr_request_id=qrid,
            service_id=service_id,
            service_name=service_name,
            purpose=purpose,
            requested_claims=requested_claims,
            nonce=nonce,
            expires_at=exp,
            signature=sig
        )
        qr_uri = f"digiin://service-verify/{qrid}?service={service_id}&nonce={nonce}"
        return req, qr_uri

class ServiceDashboardService:
    def __init__(self):
        pass

    @staticmethod
    def compute_service_metrics(requests: list[ServiceVerificationRequest]) -> dict[str, Any]:
        total = len(requests)
        pending = len([r for r in requests if r.status in (RequestLifecycleStatus.CREATED, RequestLifecycleStatus.DELIVERED, RequestLifecycleStatus.VIEWED, RequestLifecycleStatus.APPROVED, RequestLifecycleStatus.VERIFYING)])
        completed = len([r for r in requests if r.status == RequestLifecycleStatus.COMPLETED])
        failed = len([r for r in requests if r.status in (RequestLifecycleStatus.FAILED, RequestLifecycleStatus.DENIED)])
        expired = len([r for r in requests if r.status in (RequestLifecycleStatus.EXPIRED, RequestLifecycleStatus.CANCELLED)])

        success_rate = (completed / total * 100) if total > 0 else 100.0

        return {
            "totalRequests": total,
            "pending": pending,
            "completed": completed,
            "failed": failed,
            "expired": expired,
            "successRatePercent": round(success_rate, 1)
        }
