"""
DigiIn Controlled Pilot & Production Validation — Organization Onboarding Workflow
Enforces a formal 8-point verification and configuration checklist before activating pilot organizations.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


class OrgStatus:
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    OFFBOARDED = "OFFBOARDED"

@dataclass
class PilotOrganization:
    organization_id: str
    legal_name: str
    display_name: str
    status: str = OrgStatus.PENDING
    admins: list[str] = field(default_factory=list)
    allowed_verification_types: list[str] = field(default_factory=list)
    allowed_scopes: list[str] = field(default_factory=list)
    checklist: dict[str, bool] = field(default_factory=dict)
    activated_at: float | None = None

REQUIRED_CHECKLIST_ITEMS = [
    "identity_verified",
    "admin_verified",
    "scopes_approved",
    "provider_access_configured",
    "callback_urls_configured",
    "security_contact_registered",
    "privacy_contact_registered",
    "test_verification_completed",
]

class OrganizationOnboardingWorkflow:
    def __init__(self):
        self._orgs: dict[str, PilotOrganization] = {}

    def register_organization(
        self,
        org_id: str,
        legal_name: str,
        display_name: str,
        admin_id: str,
        allowed_types: list[str],
        allowed_scopes: list[str]
    ) -> PilotOrganization:
        org = PilotOrganization(
            organization_id=org_id,
            legal_name=legal_name,
            display_name=display_name,
            admins=[admin_id],
            allowed_verification_types=allowed_types,
            allowed_scopes=allowed_scopes,
            checklist={item: False for item in REQUIRED_CHECKLIST_ITEMS}
        )
        self._orgs[org_id] = org
        return org

    def complete_checklist_item(self, org_id: str, checklist_key: str) -> bool:
        org = self._orgs.get(org_id)
        if not org or checklist_key not in org.checklist:
            return False
        org.checklist[checklist_key] = True
        return True

    def activate_organization(self, org_id: str) -> tuple[bool, str, PilotOrganization | None]:
        org = self._orgs.get(org_id)
        if not org:
            return False, "ORGANIZATION_NOT_FOUND", None

        # Validate all 8 checklist items
        incomplete = [k for k, v in org.checklist.items() if not v]
        if incomplete:
            return False, f"INCOMPLETE_ONBOARDING_CHECKLIST: Missing requirements: {', '.join(incomplete)}", org

        org.status = OrgStatus.ACTIVE
        org.activated_at = time.time()
        return True, "ORGANIZATION_ACTIVATED_FOR_PILOT", org
