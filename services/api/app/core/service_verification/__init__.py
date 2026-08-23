"""
DigiIn Service Verification Subsystem (Phase 33)
Provides Service Registry, Service Authentication, 8-stage Verification Request State Machine, Citizen Request Inbox, Workflow Coordinator, QR Requests, and Service Dashboard Telemetry.
"""

from .citizen_request_inbox import (
    CitizenRequestInbox,
)
from .qr_service_verification import (
    QRServiceRequest,
    QRServiceVerifier,
    ServiceDashboardService,
)
from .service_registry import (
    DigiInService,
    ServiceContext,
    ServiceRegistry,
    ServiceStatus,
)
from .verification_request_model import (
    VALID_LIFECYCLE_TRANSITIONS,
    RequestLifecycleStatus,
    ServiceVerificationRequest,
)
from .verification_workflow_coordinator import (
    ServiceVerificationCoordinator,
    ServiceVerificationResult,
)

__all__ = [
    "ServiceStatus",
    "DigiInService",
    "ServiceContext",
    "ServiceRegistry",
    "RequestLifecycleStatus",
    "VALID_LIFECYCLE_TRANSITIONS",
    "ServiceVerificationRequest",
    "CitizenRequestInbox",
    "ServiceVerificationResult",
    "ServiceVerificationCoordinator",
    "QRServiceRequest",
    "QRServiceVerifier",
    "ServiceDashboardService",
]
