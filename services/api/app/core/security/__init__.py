"""Phase 8 — Security package.

Re-exports everything from the original core/security.py (now auth.py)
so all existing imports of `from app.core.security import create_access_token` continue to work.
"""

# Re-export auth functions (original security.py contents)
from app.core.security.audit_chain import (  # noqa: F401
    AuditChain,
    SecurityAuditEventType,
    audit_chain,
)
from app.core.security.auth import (  # noqa: F401
    AUTH_AUDIENCE,
    AUTH_ISSUER,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

# Phase 8 security modules
from app.core.security.classification import (  # noqa: F401
    ClassificationGuard,
    ClassificationPolicy,
    DataClassification,
)
from app.core.security.encryption import EnvelopeEncryptor, envelope_encryptor  # noqa: F401
from app.core.security.key_registry import KeyPurpose, KeyRegistry, key_registry  # noqa: F401
from app.core.security.policy import PolicyEffect, PolicyEngine, policy_engine  # noqa: F401
from app.core.security.privacy import (  # noqa: F401
    MinimalDisclosure,
    PIIDetector,
    PredicateEvaluator,
    minimal_disclosure,
    pii_detector,
    predicate_evaluator,
)
from app.core.security.rate_limits import (  # noqa: F401
    MultiDimensionRateLimiter,
    RateLimitPolicy,
    rate_limiter,
)
from app.core.security.retention import (  # noqa: F401
    RetentionEngine,
    SecureDeletionOrchestrator,
    retention_engine,
)

__all__ = [
    # Auth (from auth.py)
    "AUTH_ISSUER", "AUTH_AUDIENCE",
    "hash_password", "verify_password",
    "create_access_token", "create_refresh_token", "decode_token",
    # Phase 8
    "DataClassification", "ClassificationPolicy", "ClassificationGuard",
    "KeyRegistry", "KeyPurpose", "key_registry",
    "EnvelopeEncryptor", "envelope_encryptor",
    "PolicyEngine", "PolicyEffect", "policy_engine",
    "AuditChain", "SecurityAuditEventType", "audit_chain",
    "RetentionEngine", "SecureDeletionOrchestrator", "retention_engine",
    "MultiDimensionRateLimiter", "RateLimitPolicy", "rate_limiter",
    "MinimalDisclosure", "PIIDetector", "PredicateEvaluator",
]
