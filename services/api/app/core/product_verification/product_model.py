"""
DigiIn Product Verification — Generic Product Model & Identity
Defines generic DigiIn product artifacts (credentials, certificates, badges, claims, records)
and generates high-entropy opaque identifiers (DGP-XXXX-XXXX-XXXX).
"""

from __future__ import annotations

import re
import secrets
import time
from dataclasses import dataclass, field
from typing import Any

PRODUCT_ID_PATTERN = re.compile(r"^DGP-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$")

class ProductType:
    VERIFIABLE_CREDENTIAL = "VERIFIABLE_CREDENTIAL"
    DIGITAL_CERTIFICATE = "DIGITAL_CERTIFICATE"
    VERIFICATION_BADGE = "VERIFICATION_BADGE"
    DIGITAL_RECORD = "DIGITAL_RECORD"
    SERVICE_CLAIM = "SERVICE_CLAIM"

class ProductStatus:
    ISSUED = "ISSUED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"
    SUPERSEDED = "SUPERSEDED"
    UNKNOWN = "UNKNOWN"

@dataclass
class DigiInProduct:
    product_id: str
    product_type: str
    issuer_id: str
    subject_id: str | None
    schema_version: str
    claims: dict[str, Any]
    status: str = ProductStatus.ACTIVE
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    revoked_at: float | None = None
    revocation_reason: str | None = None
    superseded_by: str | None = None
    version: str = "1.0.0"

    @staticmethod
    def generate_product_id() -> str:
        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        p1 = "".join(secrets.choice(chars) for _ in range(4))
        p2 = "".join(secrets.choice(chars) for _ in range(4))
        p3 = "".join(secrets.choice(chars) for _ in range(4))
        return f"DGP-{p1}-{p2}-{p3}"

    @staticmethod
    def is_valid_product_id(product_id: str) -> bool:
        return bool(PRODUCT_ID_PATTERN.match(product_id))
