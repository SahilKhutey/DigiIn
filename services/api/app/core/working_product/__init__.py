"""
DigiIn Working Product & User Request Handling Subsystem (Phase 31)
Provides standardized request envelopes, user action routers, auth contexts, document workflows, consent workflows, credential presentations, notifications, activity history, and error sanitization.
"""

from .action_router import (
    UserActionRouter,
    UserActionTypes,
)
from .auth_context import (
    AuthContext,
    AuthorizationGuard,
)
from .consent_workflow import (
    InstitutionalConsentWorkflow,
    VerificationConsentRequest,
)
from .credential_presentation_workflow import (
    CredentialPresentationWorkflow,
    ProductCredential,
)
from .document_verification_workflow import (
    DocumentVerificationWorkflow,
    UploadedDocument,
)
from .error_handling import (
    DigiInError,
    ErrorSanitizer,
)
from .notification_and_activity import (
    ActivityHistoryManager,
    ActivityItem,
    InAppNotification,
    NotificationManager,
)
from .request_pipeline import (
    Actor,
    DigiInRequest,
    DigiInResponse,
    IdempotencyManager,
    RequestStatus,
)

__all__ = [
    "RequestStatus",
    "Actor",
    "DigiInRequest",
    "DigiInResponse",
    "IdempotencyManager",
    "AuthContext",
    "AuthorizationGuard",
    "UserActionTypes",
    "UserActionRouter",
    "UploadedDocument",
    "DocumentVerificationWorkflow",
    "VerificationConsentRequest",
    "InstitutionalConsentWorkflow",
    "ProductCredential",
    "CredentialPresentationWorkflow",
    "ActivityItem",
    "InAppNotification",
    "ActivityHistoryManager",
    "NotificationManager",
    "DigiInError",
    "ErrorSanitizer",
]
