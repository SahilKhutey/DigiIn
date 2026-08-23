"""
DigiIn Long-Term Infrastructure — Canonical Trust Model & Identity Layer
Defines permanent core entities (Subject, Account, PortableCredential, Claim, Proof, Presentation, Consent)
and enforces stable, opaque non-semantic Account ID generation (DGI-XXXXXXXXXXXX).
"""

from __future__ import annotations

import re
import secrets
import time
from dataclasses import dataclass, field
from typing import Any

ACCOUNT_ID_PATTERN = re.compile(r"^DGI-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$")

class CredentialStatus:
    ISSUED = "ISSUED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    SUPERSEDED = "SUPERSEDED"

@dataclass
class DigiInAccount:
    account_id: str
    status: str = "ACTIVE"
    created_at: float = field(default_factory=time.time)

    @staticmethod
    def generate_id() -> str:
        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # Crockford Base32-inspired without ambiguous chars
        p1 = "".join(secrets.choice(chars) for _ in range(4))
        p2 = "".join(secrets.choice(chars) for _ in range(4))
        p3 = "".join(secrets.choice(chars) for _ in range(4))
        return f"DGI-{p1}-{p2}-{p3}"

    @staticmethod
    def is_valid_id(account_id: str) -> bool:
        return bool(ACCOUNT_ID_PATTERN.match(account_id))

@dataclass
class PortableCredential:
    id: str
    issuer_id: str
    subject_id: str
    credential_type: str  # e.g., "education.degree"
    schema_version: str = "1.0.0"
    claims: dict[str, Any] = field(default_factory=dict)
    status: str = CredentialStatus.ACTIVE
    issued_at: float = field(default_factory=time.time)
    valid_until: float | None = None
    supersedes_id: str | None = None
    superseded_by: str | None = None

class PortableCredentialManager:
    def __init__(self):
        self._credentials: dict[str, PortableCredential] = {}

    def issue_credential(
        self,
        issuer_id: str,
        subject_id: str,
        cred_type: str,
        claims: dict[str, Any],
        schema_version: str = "1.0.0",
        valid_days: int = 365
    ) -> PortableCredential:
        cid = f"cred_{secrets.token_hex(10)}"
        cred = PortableCredential(
            id=cid,
            issuer_id=issuer_id,
            subject_id=subject_id,
            credential_type=cred_type,
            schema_version=schema_version,
            claims=claims,
            status=CredentialStatus.ACTIVE,
            valid_until=time.time() + (valid_days * 86400)
        )
        self._credentials[cid] = cred
        return cred

    def supersede_credential(
        self,
        old_cred_id: str,
        issuer_id: str,
        updated_claims: dict[str, Any]
    ) -> tuple[bool, PortableCredential | None, str | None]:
        old_cred = self._credentials.get(old_cred_id)
        if not old_cred:
            return False, None, "OLD_CREDENTIAL_NOT_FOUND"
        if old_cred.issuer_id != issuer_id:
            return False, None, "UNAUTHORIZED_ISSUER_MISMATCH"

        # Create new credential
        new_cred = self.issue_credential(
            issuer_id=issuer_id,
            subject_id=old_cred.subject_id,
            cred_type=old_cred.credential_type,
            claims=updated_claims,
            schema_version=old_cred.schema_version
        )
        new_cred.supersedes_id = old_cred_id

        # Update old credential without destroying history
        old_cred.status = CredentialStatus.SUPERSEDED
        old_cred.superseded_by = new_cred.id
        return True, new_cred, None

    def revoke_credential(self, cred_id: str, issuer_id: str, reason: str = "AUTHORITATIVE_REVOCATION") -> bool:
        cred = self._credentials.get(cred_id)
        if not cred or cred.issuer_id != issuer_id:
            return False
        cred.status = CredentialStatus.REVOKED
        return True

    def get_credential(self, cred_id: str) -> PortableCredential | None:
        return self._credentials.get(cred_id)
