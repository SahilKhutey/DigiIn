"""
DigiIn Working Product — Authentication Context & Granular Authorization
Provides normalized security context and enforces fine-grained resource and purpose authorizations.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class AuthContext:
    user_id: str
    account_id: str
    roles: list[str]
    organization_ids: list[str]
    permissions: set[str]
    session_id: str
    authenticated_at: float = field(default_factory=time.time)

class AuthorizationGuard:
    @staticmethod
    def is_authorized(
        auth_context: AuthContext,
        required_permission: str,
        resource_owner_id: str | None = None
    ) -> tuple[bool, str | None]:
        # 1. Check if user holds the permission
        if required_permission not in auth_context.permissions and "*" not in auth_context.permissions:
            return False, f"PERMISSION_DENIED: User lacks '{required_permission}'"

        # 2. Enforce resource ownership if applicable
        if resource_owner_id and resource_owner_id != auth_context.user_id and resource_owner_id != auth_context.account_id:
            # Check if actor is an admin
            if "ADMIN" not in auth_context.roles and "SYSTEM" not in auth_context.roles:
                return False, "RESOURCE_OWNERSHIP_DENIED: Cannot operate on another citizen's resource"

        return True, None
