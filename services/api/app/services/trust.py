"""Trust and consent models for synthetic prototype journeys."""

from app.domain.models import ConsentPreview, IssuerHealth
from app.integrations.issuer import MockIssuerAdapter

ISSUERS = [
    MockIssuerAdapter("mock-cbse", "Mock CBSE", "healthy", 420),
    MockIssuerAdapter("mock-transport", "Mock Transport", "healthy", 260),
    MockIssuerAdapter("mock-state-university", "Mock State University", "degraded", 1_850),
]


def issuer_health() -> list[IssuerHealth]:
    return [issuer.health() for issuer in ISSUERS]


def consent_preview() -> ConsentPreview:
    return ConsentPreview(
        requesterName="Demo education portal",
        purpose="Verify an education credential for a demonstration application.",
        scopes=["Class XII marksheet", "Document verification status"],
        access="One-time access",
        retentionNotice="In production, the requester must declare its retention policy before consent is granted.",
    )
