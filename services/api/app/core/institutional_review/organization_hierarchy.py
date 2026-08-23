"""
DigiIn Institutional Review — Organization & Department Hierarchy Layer
Defines organizations, departments, institutional users, and role-based access control (RBAC).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


class OrganizationType:
    GOVERNMENT = "GOVERNMENT"
    UNIVERSITY = "UNIVERSITY"
    EMPLOYER = "EMPLOYER"
    FINANCIAL = "FINANCIAL"
    HEALTHCARE = "HEALTHCARE"
    OTHER = "OTHER"

class OrganizationStatus:
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"

class DepartmentStatus:
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"

class OrganizationRole:
    ORG_ADMIN = "ORG_ADMIN"
    DEPARTMENT_ADMIN = "DEPARTMENT_ADMIN"
    REVIEWER = "REVIEWER"
    OPERATOR = "OPERATOR"
    VIEWER = "VIEWER"

ROLE_PERMISSIONS: dict[str, set[str]] = {
    OrganizationRole.ORG_ADMIN: {"requests:create", "requests:read", "requests:review", "decisions:create", "users:manage", "templates:manage", "settings:manage"},
    OrganizationRole.DEPARTMENT_ADMIN: {"requests:create", "requests:read", "requests:review", "decisions:create", "templates:manage"},
    OrganizationRole.REVIEWER: {"requests:read", "requests:review", "decisions:create"},
    OrganizationRole.OPERATOR: {"requests:create", "requests:read"},
    OrganizationRole.VIEWER: {"requests:read"},
}

@dataclass
class Organization:
    id: str
    name: str
    type: str
    status: str = OrganizationStatus.ACTIVE
    verified: bool = True
    created_at: float = field(default_factory=time.time)

@dataclass
class Department:
    id: str
    organization_id: str
    name: str
    code: str
    status: str = DepartmentStatus.ACTIVE
    created_at: float = field(default_factory=time.time)

@dataclass
class InstitutionalUser:
    id: str
    organization_id: str
    department_id: str | None
    user_id: str
    name: str
    role: str
    status: str = "ACTIVE"
    created_at: float = field(default_factory=time.time)

class InstitutionalRBACGuard:
    @staticmethod
    def is_authorized(user: InstitutionalUser, required_permission: str, target_department_id: str | None = None) -> tuple[bool, str]:
        # 1. Check user status
        if user.status != "ACTIVE":
            return False, "USER_SUSPENDED"

        # 2. Check permission
        user_perms = ROLE_PERMISSIONS.get(user.role, set())
        if required_permission not in user_perms:
            return False, f"PERMISSION_DENIED: Role '{user.role}' lacks '{required_permission}'"

        # 3. Check departmental scoping
        if user.role != OrganizationRole.ORG_ADMIN and target_department_id:
            if user.department_id and user.department_id != target_department_id:
                return False, "DEPARTMENT_SCOPING_DENIED: User cannot operate outside their department"

        return True, "AUTHORIZED"

class OrganizationHierarchyManager:
    def __init__(self):
        self._orgs: dict[str, Organization] = {}
        self._departments: dict[str, Department] = {}
        self._users: dict[str, InstitutionalUser] = {}
        self._seed_default_hierarchy()

    def _seed_default_hierarchy(self):
        org = Organization(
            id="org_delhi_university",
            name="University of Delhi",
            type=OrganizationType.UNIVERSITY,
            status=OrganizationStatus.ACTIVE,
            verified=True
        )
        d1 = Department(
            id="dept_admissions",
            organization_id=org.id,
            name="Admissions Division",
            code="ADM",
            status=DepartmentStatus.ACTIVE
        )
        d2 = Department(
            id="dept_scholarships",
            organization_id=org.id,
            name="Scholarship Division",
            code="SCH",
            status=DepartmentStatus.ACTIVE
        )
        u1 = InstitutionalUser(
            id="iuser_org_admin",
            organization_id=org.id,
            department_id=None,
            user_id="usr_prof_sharma",
            name="Prof. Sharma",
            role=OrganizationRole.ORG_ADMIN
        )
        u2 = InstitutionalUser(
            id="iuser_reviewer",
            organization_id=org.id,
            department_id=d1.id,
            user_id="usr_officer_verma",
            name="Officer Verma",
            role=OrganizationRole.REVIEWER
        )

        self._orgs[org.id] = org
        self._departments[d1.id] = d1
        self._departments[d2.id] = d2
        self._users[u1.id] = u1
        self._users[u2.id] = u2

    def get_organization(self, org_id: str) -> Organization | None:
        return self._orgs.get(org_id)

    def get_department(self, dept_id: str) -> Department | None:
        return self._departments.get(dept_id)

    def get_user(self, user_id: str) -> InstitutionalUser | None:
        return self._users.get(user_id)
