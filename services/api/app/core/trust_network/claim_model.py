"""
DigiIn Trust Network & Interoperability — Verified Claim Model & Issuance Engine
Manages verified claim lifecycles (ACTIVE -> EXPIRED -> REVOKED) and assurance levels.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any

from .claim_schema import ClaimSchemaRegistry
from .issuer_registry import IssuerRegistry


class ClaimStatus:
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"

class AssuranceLevel:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"

@dataclass
class VerifiedClaimRecord:
    id: str
    subject_id: str
    issuer_id: str
    claim_type: str
    value: dict[str, Any]
    status: str = ClaimStatus.ACTIVE
    schema_version: str = "1.0"
    assurance_level: str = AssuranceLevel.HIGH
    issued_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    revoked_at: float | None = None
    source_verification_id: str | None = None

class ClaimIssuanceEngine:
    def __init__(self, issuer_registry: IssuerRegistry, schema_registry: ClaimSchemaRegistry):
        self.issuer_registry = issuer_registry
        self.schema_registry = schema_registry
        self._claims_store: dict[str, VerifiedClaimRecord] = {}

    def issue_claim(
        self,
        issuer_id: str,
        subject_id: str,
        claim_type: str,
        value: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
        schema_version: str = "1.0",
        ttl_seconds: int = 86400 * 365,
        source_verification_id: str | None = None
    ) -> tuple[bool, str | None, VerifiedClaimRecord | None]:
        claim_value = value if value is not None else (payload or {})
        # 1. Check Issuer Authority
        if not self.issuer_registry.is_issuer_authorized_for_claim(issuer_id, claim_type):
            return False, f"ISSUER_UNAUTHORIZED: Issuer '{issuer_id}' is not accredited to issue '{claim_type}'.", None

        # 2. Validate against schema
        ok, err = self.schema_registry.validate_claim_payload(claim_type, claim_value, schema_version)
        if not ok:
            return False, err, None

        cid = f"clm_{secrets.token_hex(10)}"
        now = time.time()
        record = VerifiedClaimRecord(
            id=cid,
            subject_id=subject_id,
            issuer_id=issuer_id,
            claim_type=claim_type,
            value=claim_value,
            status=ClaimStatus.ACTIVE,
            schema_version=schema_version,
            assurance_level=AssuranceLevel.VERY_HIGH,
            issued_at=now,
            expires_at=now + ttl_seconds,
            source_verification_id=source_verification_id or f"vreq_{secrets.token_hex(6)}"
        )
        self._claims_store[cid] = record
        return True, None, record

    def get_claim(self, claim_id: str) -> VerifiedClaimRecord | None:
        return self._claims_store.get(claim_id)

    def revoke_claim(self, claim_id: str, reason: str = "ISSUER_REVOCATION") -> bool:
        c = self._claims_store.get(claim_id)
        if not c or c.status != ClaimStatus.ACTIVE:
            return False
        c.status = ClaimStatus.REVOKED
        c.revoked_at = time.time()
        return True

    def check_claim_status(self, claim_id: str) -> str:
        c = self.get_claim(claim_id)
        if not c:
            return "UNKNOWN"
        if c.status == ClaimStatus.ACTIVE and c.expires_at and time.time() > c.expires_at:
            c.status = ClaimStatus.EXPIRED
        return c.status
