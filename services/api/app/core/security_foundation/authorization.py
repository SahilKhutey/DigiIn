"""
DigiIn Core Security Subsystem — RBAC & Resource Ownership Authorization
Enforces granular role permissions and prevents Insecure Direct Object References (IDOR).
"""

from typing import Any


class Role:
    CITIZEN = "CITIZEN"
    ORG_USER = "ORG_USER"
    ORG_ADMIN = "ORG_ADMIN"
    REVIEWER = "REVIEWER"
    ADMIN = "ADMIN"
    DEVELOPER = "DEVELOPER"

class Permission:
    DOCUMENT_READ = "document:read"
    DOCUMENT_UPLOAD = "document:upload"
    DOCUMENT_DELETE = "document:delete"

    VERIFICATION_CREATE = "verification:create"
    VERIFICATION_READ = "verification:read"

    CONSENT_CREATE = "consent:create"
    CONSENT_REVOKE = "consent:revoke"

    PROOF_CREATE = "proof:create"
    PROOF_VERIFY = "proof:verify"

    API_MANAGE = "api:manage"
    AUDIT_READ = "audit:read"
    SYSTEM_ADMIN = "system:admin"

ROLE_PERMISSIONS: dict[str, set[str]] = {
    Role.CITIZEN: {
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPLOAD,
        Permission.DOCUMENT_DELETE,
        Permission.CONSENT_CREATE,
        Permission.CONSENT_REVOKE,
        Permission.PROOF_CREATE,
        Permission.PROOF_VERIFY,
    },
    Role.ORG_USER: {
        Permission.VERIFICATION_CREATE,
        Permission.VERIFICATION_READ,
        Permission.PROOF_VERIFY,
    },
    Role.ORG_ADMIN: {
        Permission.VERIFICATION_CREATE,
        Permission.VERIFICATION_READ,
        Permission.PROOF_VERIFY,
        Permission.API_MANAGE,
        Permission.AUDIT_READ,
    },
    Role.REVIEWER: {
        Permission.DOCUMENT_READ,
        Permission.VERIFICATION_READ,
        Permission.VERIFICATION_CREATE,
    },
    Role.DEVELOPER: {
        Permission.PROOF_VERIFY,
        Permission.API_MANAGE,
    },
    Role.ADMIN: {
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPLOAD,
        Permission.DOCUMENT_DELETE,
        Permission.VERIFICATION_CREATE,
        Permission.VERIFICATION_READ,
        Permission.CONSENT_CREATE,
        Permission.CONSENT_REVOKE,
        Permission.PROOF_CREATE,
        Permission.PROOF_VERIFY,
        Permission.API_MANAGE,
        Permission.AUDIT_READ,
        Permission.SYSTEM_ADMIN,
    }
}

class AuthorizationService:
    @staticmethod
    def has_permission(role: str, permission: str) -> bool:
        """Check if a role possesses a specific permission."""
        perms = ROLE_PERMISSIONS.get(role, set())
        return permission in perms

    @staticmethod
    def authorize_action(actor: dict[str, Any], permission: str) -> bool:
        """Verify actor has required role permission."""
        role = actor.get("role")
        if not role:
            return False
        return AuthorizationService.has_permission(role, permission)

    @staticmethod
    def authorize_resource_access(
        actor: dict[str, Any],
        permission: str,
        resource: dict[str, Any]
    ) -> tuple[bool, str | None]:
        """
        Verify both role permission AND resource ownership/tenant boundary.
        Prevents IDOR (Insecure Direct Object Reference).
        """
        # Step 1: Role permission check
        role = actor.get("role")
        if not AuthorizationService.has_permission(role, permission):
            return False, f"FORBIDDEN: Role '{role}' lacks permission '{permission}'."

        # Super-admin bypass for system admin tasks
        if role == Role.ADMIN and permission == Permission.SYSTEM_ADMIN:
            return True, None

        # Step 2: Citizen Resource Ownership Check
        if role == Role.CITIZEN:
            owner_id = resource.get("citizen_id") or resource.get("user_id") or resource.get("citizenId")
            actor_id = actor.get("user_id") or actor.get("id") or actor.get("digiinId")
            if owner_id and actor_id and str(owner_id) != str(actor_id):
                return False, "FORBIDDEN_IDOR: Cannot access resource belonging to another citizen."

        # Step 3: Organisation Multi-Tenant Scoping Check
        if role in (Role.ORG_USER, Role.ORG_ADMIN, Role.DEVELOPER):
            resource_org_id = resource.get("organisation_id") or resource.get("organisationId")
            actor_org_id = actor.get("organisation_id") or actor.get("organisationId")
            if resource_org_id and actor_org_id and str(resource_org_id) != str(actor_org_id):
                return False, "FORBIDDEN_TENANT_ISOLATION: Cannot access resource belonging to another organisation."

        return True, None
