"""
DigiIn Developer Platform — Domain Data Models
Defines developer organizations, applications, client credentials, consent grants, and usage metrics.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DeveloperOrganization:
    id: str
    name: str
    type: str  # "GOVERNMENT" | "INSTITUTION" | "UNIVERSITY" | "ENTERPRISE" | "DEVELOPER"
    status: str = "ACTIVE"  # "PENDING" | "ACTIVE" | "SUSPENDED" | "REVOKED"
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "createdAt": self.created_at,
        }

@dataclass
class DeveloperApplication:
    id: str
    organization_id: str
    name: str
    client_id: str
    client_secret_hash: str
    environment: str = "PRODUCTION"  # "SANDBOX" | "PRODUCTION"
    status: str = "ACTIVE"            # "ACTIVE" | "SUSPENDED" | "REVOKED"
    redirect_uris: list[str] = field(default_factory=list)
    scopes: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "organizationId": self.organization_id,
            "name": self.name,
            "clientId": self.client_id,
            "environment": self.environment,
            "status": self.status,
            "scopes": self.scopes,
            "createdAt": self.created_at,
        }

@dataclass
class ConsentGrant:
    id: str
    subject_id: str
    application_id: str
    claims: list[str]
    purpose: str
    status: str = "GRANTED"  # "GRANTED" | "REVOKED" | "EXPIRED"
    granted_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    revoked_at: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "subjectId": self.subject_id,
            "applicationId": self.application_id,
            "claims": self.claims,
            "purpose": self.purpose,
            "status": self.status,
            "grantedAt": self.granted_at,
            "expiresAt": self.expires_at,
            "revokedAt": self.revoked_at,
        }

@dataclass
class ApiUsageRecord:
    application_id: str
    endpoint: str
    status_code: int
    latency_ms: float
    timestamp: float = field(default_factory=time.time)
