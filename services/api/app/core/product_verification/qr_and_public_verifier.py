"""
DigiIn Product Verification — QR Reference & Public Verification Sanitizer
Handles digiin://verify/DGP-... QR payloads and sanitizes public verification responses against data enumeration.
"""

from __future__ import annotations

from typing import Any

from .verification_engine import ProductVerificationResponse


class QRVerifierHelper:
    @staticmethod
    def generate_qr_payload(product_id: str) -> str:
        return f"digiin://verify/{product_id}"

    @staticmethod
    def parse_qr_payload(qr_string: str) -> str | None:
        if qr_string.startswith("digiin://verify/"):
            return qr_string.replace("digiin://verify/", "").strip()
        return None

class PublicResponseSanitizer:
    @staticmethod
    def sanitize_for_public(response: ProductVerificationResponse) -> dict[str, Any]:
        """Shields sensitive internal database structures and private metadata from public verification queries."""
        return {
            "verificationId": response.verification_id,
            "status": response.status,
            "assuranceLevel": response.assurance_level,
            "productType": response.product.get("type", "UNKNOWN"),
            "issuerId": response.issuer.get("id", "UNKNOWN"),
            "verifiedAt": response.verified_at,
            "reason": response.reason
        }
