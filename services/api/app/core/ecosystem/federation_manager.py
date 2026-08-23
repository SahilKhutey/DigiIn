"""
DigiIn Trust Network Expansion — Federation Manager & Institutional Readiness
Manages multi-organization trust federations, membership lifecycles, and institutional readiness scoring across 6 dimensions.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any


class FederationStatus:
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"

class MembershipRole:
    ADMIN = "ADMIN"
    ISSUER = "ISSUER"
    VERIFIER = "VERIFIER"
    BOTH = "BOTH"

class MembershipStatus:
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REMOVED = "REMOVED"

@dataclass
class FederationMembership:
    id: str
    federation_id: str
    organization_id: str
    role: str = MembershipRole.ISSUER
    status: str = MembershipStatus.ACTIVE
    joined_at: float = field(default_factory=time.time)

@dataclass
class TrustFederation:
    id: str
    name: str
    description: str
    admin_org_id: str
    status: str = FederationStatus.ACTIVE
    supported_claim_types: list[str] = field(default_factory=list)
    assurance_requirements: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

class OrganizationReadinessScorer:
    """Evaluates 6 core dimensions: Identity, Authority, Security, Privacy, Integration, Operations."""
    @staticmethod
    def calculate_readiness(dimensions: dict[str, bool]) -> tuple[bool, dict[str, Any]]:
        required = ["identity", "authority", "security", "privacy", "integration", "operations"]
        missing = [r for r in required if not dimensions.get(r, False)]
        ready = len(missing) == 0
        return ready, {
            "isReady": ready,
            "missingDimensions": missing,
            "completionPct": f"{round(((len(required) - len(missing)) / len(required)) * 100.0, 1)}%"
        }

class FederationManager:
    def __init__(self):
        self._federations: dict[str, TrustFederation] = {}
        self._memberships: dict[str, list[FederationMembership]] = {}
        self._seed_default_federation()

    def _seed_default_federation(self):
        fid = "fed_higher_education_india"
        fed = TrustFederation(
            id=fid,
            name="National Higher Education Trust Federation",
            description="Federated academic credential verification network",
            admin_org_id="org_ministry_education",
            status=FederationStatus.ACTIVE,
            supported_claim_types=["education.degree", "education.transcript"],
            assurance_requirements=["A3_HIGH_ASSURANCE", "A4_REGULATED"]
        )
        self._federations[fid] = fed
        self._memberships[fid] = [
            FederationMembership(id="mem_01", federation_id=fid, organization_id="org_delhi_univ", role=MembershipRole.ISSUER),
            FederationMembership(id="mem_02", federation_id=fid, organization_id="org_ministry_education", role=MembershipRole.ADMIN),
        ]

    def create_federation(
        self,
        name: str,
        description: str,
        admin_org_id: str,
        supported_claims: list[str],
        assurance_reqs: list[str]
    ) -> TrustFederation:
        fid = f"fed_{secrets.token_hex(8)}"
        fed = TrustFederation(
            id=fid,
            name=name,
            description=description,
            admin_org_id=admin_org_id,
            supported_claim_types=supported_claims,
            assurance_requirements=assurance_reqs
        )
        self._federations[fid] = fed
        self._memberships[fid] = []
        return fed

    def add_member(self, federation_id: str, organization_id: str, role: str) -> tuple[bool, str, FederationMembership | None]:
        fed = self._federations.get(federation_id)
        if not fed or fed.status != FederationStatus.ACTIVE:
            return False, "FEDERATION_NOT_ACTIVE_OR_FOUND", None

        mem_id = f"mem_{secrets.token_hex(8)}"
        membership = FederationMembership(
            id=mem_id,
            federation_id=federation_id,
            organization_id=organization_id,
            role=role,
            status=MembershipStatus.ACTIVE
        )
        if federation_id not in self._memberships:
            self._memberships[federation_id] = []
        self._memberships[federation_id].append(membership)
        return True, "MEMBERSHIP_ACTIVATED", membership

    def is_organization_in_federation(self, federation_id: str, organization_id: str) -> bool:
        members = self._memberships.get(federation_id, [])
        return any(m.organization_id == organization_id and m.status == MembershipStatus.ACTIVE for m in members)
