"""
DigiIn Developer Platform — Multi-Tenant Isolation Guard
Enforces strict boundary checks ensuring Organization A cannot access Organization B's applications, verifications, proofs, or webhooks.
"""

from __future__ import annotations


class MultiTenantIsolationError(Exception):
    pass

class MultiTenantGuard:
    @staticmethod
    def enforce_application_ownership(application_org_id: str, caller_org_id: str):
        if application_org_id != caller_org_id:
            raise MultiTenantIsolationError(
                f"TENANT_ISOLATION_VIOLATION: Organization '{caller_org_id}' is unauthorized to access resources belonging to '{application_org_id}'."
            )

    @staticmethod
    def enforce_resource_ownership(resource_org_id: str, caller_org_id: str):
        if resource_org_id != caller_org_id:
            raise MultiTenantIsolationError(
                f"TENANT_ISOLATION_VIOLATION: Cross-organization access to resource rejected (Caller: {caller_org_id}, Owner: {resource_org_id})."
            )
