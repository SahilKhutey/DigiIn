"""
DigiIn Product Verification — Multi-Point Verification Check Units
Encapsulates individual verification checks: ProductExists, IssuerTrust, Signature, Integrity, Expiration, Revocation, Policy.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from .product_crypto import ProductCryptoEngine, ProductSignature
from .product_model import DigiInProduct, ProductStatus


@dataclass
class CheckResult:
    check_name: str
    passed: bool
    code: str
    message: str

class VerificationCheckUnits:
    @staticmethod
    def check_product_exists(product_record: Any | None) -> CheckResult:
        if not product_record:
            return CheckResult("PRODUCT_EXISTS", False, "PRODUCT_NOT_FOUND", "Product does not exist in registry.")
        return CheckResult("PRODUCT_EXISTS", True, "PRODUCT_FOUND", "Product record resolved.")

    @staticmethod
    def check_issuer_trust(issuer_id: str, trust_registry: Any) -> CheckResult:
        trusted = trust_registry.is_trusted(issuer_id) if hasattr(trust_registry, "is_trusted") else True
        if not trusted:
            return CheckResult("ISSUER_TRUST", False, "ISSUER_NOT_TRUSTED", f"Issuer '{issuer_id}' is not accredited.")
        return CheckResult("ISSUER_TRUST", True, "ISSUER_ACCREDITED", f"Issuer '{issuer_id}' is trusted.")

    @staticmethod
    def check_signature_and_integrity(product: DigiInProduct, signature: ProductSignature, public_key: Any | None = None) -> CheckResult:
        payload_to_verify = {
            "productId": product.product_id,
            "productType": product.product_type,
            "issuerId": product.issuer_id,
            "subjectId": product.subject_id,
            "claims": product.claims,
            "schemaVersion": product.schema_version,
            "createdAt": product.created_at
        }
        valid = ProductCryptoEngine.verify_product_signature(payload_to_verify, signature, public_key)
        if not valid:
            return CheckResult("SIGNATURE_INTEGRITY", False, "INVALID_SIGNATURE", "Cryptographic signature or digest failed.")
        return CheckResult("SIGNATURE_INTEGRITY", True, "SIGNATURE_VALID", "Cryptographic signature and digest verified.")

    @staticmethod
    def check_status_and_lifecycle(product: DigiInProduct) -> CheckResult:
        now = time.time()
        if product.status == ProductStatus.REVOKED:
            return CheckResult("LIFECYCLE_STATUS", False, "PRODUCT_REVOKED", f"Product was revoked on {product.revoked_at}")
        if product.status == ProductStatus.SUSPENDED:
            return CheckResult("LIFECYCLE_STATUS", False, "PRODUCT_SUSPENDED", "Product is temporarily suspended.")
        if product.expires_at and product.expires_at < now:
            return CheckResult("LIFECYCLE_STATUS", False, "PRODUCT_EXPIRED", "Product validity period has ended.")
        if product.status != ProductStatus.ACTIVE:
            return CheckResult("LIFECYCLE_STATUS", False, "STATUS_NOT_ACTIVE", f"Product status is {product.status}")

        return CheckResult("LIFECYCLE_STATUS", True, "STATUS_ACTIVE", "Product is active and unrevoked.")
