"""
DigiIn Product Verification Subsystem (Phase 32)
Provides generic product artifacts, opaque identifiers (DGP-XXXX-XXXX-XXXX), Ed25519 signing, 7-point verification checks, product lifecycle management, QR references, and public verification sanitization.
"""

from .product_crypto import (
    ProductCryptoEngine,
    ProductSignature,
)
from .product_lifecycle import (
    ProductLifecycleManager,
    ProductRecord,
)
from .product_model import (
    PRODUCT_ID_PATTERN,
    DigiInProduct,
    ProductStatus,
    ProductType,
)
from .qr_and_public_verifier import (
    PublicResponseSanitizer,
    QRVerifierHelper,
)
from .verification_checks import (
    CheckResult,
    VerificationCheckUnits,
)
from .verification_engine import (
    ProductVerificationEngine,
    ProductVerificationRequest,
    ProductVerificationResponse,
    VerificationOutcomeStatus,
)

__all__ = [
    "PRODUCT_ID_PATTERN",
    "ProductType",
    "ProductStatus",
    "DigiInProduct",
    "ProductSignature",
    "ProductCryptoEngine",
    "ProductRecord",
    "ProductLifecycleManager",
    "CheckResult",
    "VerificationCheckUnits",
    "VerificationOutcomeStatus",
    "ProductVerificationRequest",
    "ProductVerificationResponse",
    "ProductVerificationEngine",
    "QRVerifierHelper",
    "PublicResponseSanitizer",
]
