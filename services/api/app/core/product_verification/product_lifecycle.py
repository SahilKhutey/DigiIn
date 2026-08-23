"""
DigiIn Product Verification — Product Lifecycle Manager
Manages product creation, signing, suspension, reactivation, revocation, and supersession.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from .product_crypto import ProductCryptoEngine, ProductSignature
from .product_model import DigiInProduct, ProductStatus


@dataclass
class ProductRecord:
    product: DigiInProduct
    signature: ProductSignature
    status_history: list[dict[str, Any]]

class ProductLifecycleManager:
    def __init__(self):
        self._records: dict[str, ProductRecord] = {}

    def create_product(
        self,
        product_type: str,
        issuer_id: str,
        subject_id: str | None,
        schema_version: str,
        claims: dict[str, Any],
        private_key: Any | None = None,
        key_id: str = "ed25519_default_key",
        valid_days: int = 365
    ) -> ProductRecord:
        pid = DigiInProduct.generate_product_id()
        now = time.time()

        product = DigiInProduct(
            product_id=pid,
            product_type=product_type,
            issuer_id=issuer_id,
            subject_id=subject_id,
            schema_version=schema_version,
            claims=claims,
            status=ProductStatus.ACTIVE,
            created_at=now,
            expires_at=now + (valid_days * 86400)
        )

        # Generate cryptographic signature
        payload_to_sign = {
            "productId": pid,
            "productType": product_type,
            "issuerId": issuer_id,
            "subjectId": subject_id,
            "claims": claims,
            "schemaVersion": schema_version,
            "createdAt": now
        }
        sig = ProductCryptoEngine.sign_product(payload_to_sign, private_key, key_id=key_id)

        rec = ProductRecord(
            product=product,
            signature=sig,
            status_history=[{"status": ProductStatus.ACTIVE, "timestamp": now, "reason": "INITIAL_ISSUANCE"}]
        )
        self._records[pid] = rec
        return rec

    def suspend_product(self, product_id: str, reason: str = "INVESTIGATION") -> bool:
        rec = self._records.get(product_id)
        if not rec or rec.product.status != ProductStatus.ACTIVE:
            return False
        rec.product.status = ProductStatus.SUSPENDED
        rec.status_history.append({"status": ProductStatus.SUSPENDED, "timestamp": time.time(), "reason": reason})
        return True

    def reactivate_product(self, product_id: str) -> bool:
        rec = self._records.get(product_id)
        if not rec or rec.product.status != ProductStatus.SUSPENDED:
            return False
        rec.product.status = ProductStatus.ACTIVE
        rec.status_history.append({"status": ProductStatus.ACTIVE, "timestamp": time.time(), "reason": "REINSTATED"})
        return True

    def revoke_product(self, product_id: str, reason: str = "AUTHORITATIVE_REVOCATION") -> bool:
        rec = self._records.get(product_id)
        if not rec:
            return False
        rec.product.status = ProductStatus.REVOKED
        rec.product.revoked_at = time.time()
        rec.product.revocation_reason = reason
        rec.status_history.append({"status": ProductStatus.REVOKED, "timestamp": time.time(), "reason": reason})
        return True

    def get_product(self, product_id: str) -> ProductRecord | None:
        return self._records.get(product_id)
