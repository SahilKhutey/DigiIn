"""
DigiIn Product Verification — Product Verification Engine
Orchestrates multi-point verification checks, evaluates policies, and returns standardized verification outcomes.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any

from .product_lifecycle import ProductLifecycleManager
from .verification_checks import VerificationCheckUnits


class VerificationOutcomeStatus:
    VERIFIED = "VERIFIED"
    INVALID = "INVALID"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"
    SUSPENDED = "SUSPENDED"
    UNKNOWN = "UNKNOWN"

@dataclass
class ProductVerificationRequest:
    product_id: str | None = None
    presentation: str | None = None
    qr_payload: str | None = None
    purpose: str = "GENERAL_VERIFICATION"

@dataclass
class ProductVerificationResponse:
    verification_id: str
    status: str
    assurance_level: str
    issuer: dict[str, Any]
    product: dict[str, Any]
    checks: list[dict[str, Any]]
    verified_at: float = field(default_factory=time.time)
    reason: str | None = None

class ProductVerificationEngine:
    def __init__(self, lifecycle_mgr: ProductLifecycleManager, trust_registry: Any = None):
        self.lifecycle_mgr = lifecycle_mgr
        self.trust_registry = trust_registry

    def verify_product(
        self,
        request: ProductVerificationRequest,
        public_key: Any | None = None
    ) -> ProductVerificationResponse:
        vid = f"ver_{secrets.token_hex(8)}"
        target_id = request.product_id

        # 1. Resolve product ID from QR if provided
        if not target_id and request.qr_payload:
            if request.qr_payload.startswith("digiin://verify/"):
                target_id = request.qr_payload.replace("digiin://verify/", "").strip()

        if not target_id:
            return ProductVerificationResponse(
                verification_id=vid,
                status=VerificationOutcomeStatus.UNKNOWN,
                assurance_level="NONE",
                issuer={},
                product={},
                checks=[],
                reason="MISSING_PRODUCT_IDENTIFIER"
            )

        # 2. Check existence
        rec = self.lifecycle_mgr.get_product(target_id)
        c_exist = VerificationCheckUnits.check_product_exists(rec)
        if not c_exist.passed:
            return ProductVerificationResponse(
                verification_id=vid,
                status=VerificationOutcomeStatus.UNKNOWN,
                assurance_level="NONE",
                issuer={},
                product={"id": target_id},
                checks=[{"check": c_exist.check_name, "passed": False, "code": c_exist.code}],
                reason="PRODUCT_DOES_NOT_EXIST"
            )

        product = rec.product
        signature = rec.signature

        # 3. Check Issuer Trust
        c_trust = VerificationCheckUnits.check_issuer_trust(product.issuer_id, self.trust_registry)

        # 4. Check Signature & Integrity
        c_sig = VerificationCheckUnits.check_signature_and_integrity(product, signature, public_key)

        # 5. Check Lifecycle Status
        c_status = VerificationCheckUnits.check_status_and_lifecycle(product)

        checks_summary = [
            {"check": c_exist.check_name, "passed": c_exist.passed, "code": c_exist.code},
            {"check": c_trust.check_name, "passed": c_trust.passed, "code": c_trust.code},
            {"check": c_sig.check_name, "passed": c_sig.passed, "code": c_sig.code},
            {"check": c_status.check_name, "passed": c_status.passed, "code": c_status.code},
        ]

        # Determine Final Outcome Status
        if not c_trust.passed:
            outcome = VerificationOutcomeStatus.INVALID
            reason = c_trust.message
        elif not c_sig.passed:
            outcome = VerificationOutcomeStatus.INVALID
            reason = c_sig.message
        elif not c_status.passed:
            if c_status.code == "PRODUCT_REVOKED":
                outcome = VerificationOutcomeStatus.REVOKED
            elif c_status.code == "PRODUCT_SUSPENDED":
                outcome = VerificationOutcomeStatus.SUSPENDED
            elif c_status.code == "PRODUCT_EXPIRED":
                outcome = VerificationOutcomeStatus.EXPIRED
            else:
                outcome = VerificationOutcomeStatus.INVALID
            reason = c_status.message
        else:
            outcome = VerificationOutcomeStatus.VERIFIED
            reason = "Product verified successfully with mathematical integrity."

        return ProductVerificationResponse(
            verification_id=vid,
            status=outcome,
            assurance_level="A3_HIGH_ASSURANCE" if outcome == VerificationOutcomeStatus.VERIFIED else "NONE",
            issuer={"id": product.issuer_id, "trusted": c_trust.passed},
            product={"id": product.product_id, "type": product.product_type, "version": product.version},
            checks=checks_summary,
            reason=reason
        )
