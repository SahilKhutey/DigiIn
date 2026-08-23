"""
DigiIn Institutional Scale — Institutional Role-Based Access Control (RBAC)
Governs organization permissions across 7 roles: OWNER, ADMIN, TRUST_ADMIN, SECURITY_ADMIN, DEVELOPER, AUDITOR, VIEWER.
"""

from __future__ import annotations


class OrganizationRole:
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    TRUST_ADMIN = "TRUST_ADMIN"
    SECURITY_ADMIN = "SECURITY_ADMIN"
    DEVELOPER = "DEVELOPER"
    AUDITOR = "AUDITOR"
    VIEWER = "VIEWER"

ROLE_PERMISSIONS: dict[str, set[str]] = {
    OrganizationRole.OWNER: {
        "org:manage", "org:members:write", "org:roles:write", "trust:write",
        "security:write", "dev:write", "audit:read", "claims:read"
    },
    OrganizationRole.ADMIN: {
        "org:members:write", "trust:write", "security:read", "dev:write",
        "audit:read", "claims:read"
    },
    OrganizationRole.TRUST_ADMIN: {
        "trust:write", "trust:relationships:write", "accreditation:write",
        "claims:read", "audit:read"
    },
    OrganizationRole.SECURITY_ADMIN: {
        "security:write", "credentials:write", "webhooks:write", "audit:read"
    },
    OrganizationRole.DEVELOPER: {
        "dev:write", "apps:write", "sandbox:write", "webhooks:write", "claims:read"
    },
    OrganizationRole.AUDITOR: {
        "audit:read", "org:read", "trust:read", "security:read"
    },
    OrganizationRole.VIEWER: {
        "org:read", "claims:read"
    }
}

class InstitutionalRBACGuard:
    @staticmethod
    def has_permission(role: str, permission: str) -> bool:
        perms = ROLE_PERMISSIONS.get(role, set())
        return permission in perms or "org:manage" in perms

    @staticmethod
    def validate_action(role: str, permission: str) -> tuple[bool, str | None]:
        if not InstitutionalRBACGuard.has_permission(role, permission):
            return False, f"RBAC_DENIED: Role '{role}' lacks permission '{permission}'."
        return True, None
