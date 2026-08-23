"""
DigiIn Trust Network & Interoperability — Scoped Trust Relationship Engine
Governs explicit, scoped trust agreements between Issuers and Verifiers for specific claim types and validity periods.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field


class RelationshipStatus:
    REQUESTED = "REQUESTED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"

@dataclass
class TrustRelationship:
    id: str
    source_org_id: str  # Issuer Org
    target_org_id: str  # Verifier Org
    allowed_claim_types: list[str]
    allowed_purposes: list[str]
    status: str = RelationshipStatus.REQUESTED
    valid_from: float = field(default_factory=time.time)
    valid_until: float | None = None
    created_at: float = field(default_factory=time.time)

class TrustRelationshipEngine:
    def __init__(self):
        self._relationships: dict[str, TrustRelationship] = {}
        self._seed_default_relationship()

    def _seed_default_relationship(self):
        rid = "rel_du_to_scholarship"
        rel = TrustRelationship(
            id=rid,
            source_org_id="org_delhi_univ",
            target_org_id="org_ministry_education",
            allowed_claim_types=["education.degree"],
            allowed_purposes=["SCHOLARSHIP_ELIGIBILITY"],
            status=RelationshipStatus.ACTIVE,
            valid_from=time.time(),
            valid_until=time.time() + (86400 * 365)
        )
        self._relationships[rid] = rel

    def create_relationship(
        self,
        source_org: str,
        target_org: str,
        allowed_claims: list[str],
        allowed_purposes: list[str],
        validity_days: int = 365
    ) -> TrustRelationship:
        rid = f"rel_{secrets.token_hex(8)}"
        now = time.time()
        rel = TrustRelationship(
            id=rid,
            source_org_id=source_org,
            target_org_id=target_org,
            allowed_claim_types=allowed_claims,
            allowed_purposes=allowed_purposes,
            status=RelationshipStatus.ACTIVE,
            valid_from=now,
            valid_until=now + (86400 * validity_days)
        )
        self._relationships[rid] = rel
        return rel

    def validate_relationship(
        self,
        issuer_org: str,
        verifier_org: str,
        claim_type: str,
        purpose: str
    ) -> tuple[bool, str | None]:
        matching = [
            r for r in self._relationships.values()
            if r.source_org_id == issuer_org and r.target_org_id == verifier_org
        ]
        if not matching:
            return False, "NO_TRUST_RELATIONSHIP_ESTABLISHED"

        rel = matching[-1]
        if rel.status != RelationshipStatus.ACTIVE:
            return False, f"RELATIONSHIP_NOT_ACTIVE: Current state is '{rel.status}'."

        if rel.valid_until and time.time() > rel.valid_until:
            return False, "RELATIONSHIP_EXPIRED"

        if claim_type not in rel.allowed_claim_types and "*" not in rel.allowed_claim_types:
            return False, f"CLAIM_TYPE_NOT_SCOPED: Claim '{claim_type}' is not included in this trust relationship."

        if purpose not in rel.allowed_purposes and "*" not in rel.allowed_purposes:
            return False, f"PURPOSE_NOT_SCOPED: Purpose '{purpose}' is not included in this trust relationship."

        return True, None
