"""
DigiIn Web Surfaces — Route Authentication & Navigation Guard
Enforces route access boundaries, role requirements, and redirect returns (/login?returnTo=...).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserSession:
    user_id: str
    account_id: str
    roles: set[str]  # e.g., {"CITIZEN"}, {"ORG_ADMIN"}, {"REVIEWER"}
    is_authenticated: bool = True

class RouteNavigationGuard:
    PUBLIC_ROUTES = {"/", "/about", "/how-it-works", "/services", "/organizations", "/security", "/help", "/privacy", "/terms", "/login", "/register", "/institution/login"}

    @staticmethod
    def evaluate_route_access(path: str, session: UserSession | None, required_role: str | None = None) -> tuple[bool, str | None]:
        # 1. Public route check
        if path in RouteNavigationGuard.PUBLIC_ROUTES or path.startswith("/services/"):
            return True, None

        # 2. Authenticated check
        if not session or not session.is_authenticated:
            return False, f"/login?returnTo={path}"

        # 3. Role check
        if required_role and required_role not in session.roles and "ORG_ADMIN" not in session.roles and "SYSTEM_ADMIN" not in session.roles:
            return False, "/dashboard"  # Redirect unauthorized roles back to general dashboard

        return True, None
