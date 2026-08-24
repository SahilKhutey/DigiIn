"""Phase 8.1 — Data Classification.

Every DigiIn data object receives a sensitivity classification that drives
storage, logging, access, and retention policies.

Classification hierarchy (ascending sensitivity):
  PUBLIC < INTERNAL < CONFIDENTIAL < SENSITIVE < HIGHLY_SENSITIVE < RESTRICTED

Default classification mappings:
  Public issuer metadata       → PUBLIC
  Provider configuration       → INTERNAL
  Account metadata             → SENSITIVE
  Identity claims              → HIGHLY_SENSITIVE
  Original documents           → HIGHLY_SENSITIVE
  Authentication secrets       → RESTRICTED
  Private signing keys         → RESTRICTED
"""

from __future__ import annotations

from enum import IntEnum
from typing import Any

# ---------------------------------------------------------------------------
# Sensitivity levels
# ---------------------------------------------------------------------------


class DataClassification(IntEnum):
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    SENSITIVE = 3
    HIGHLY_SENSITIVE = 4
    RESTRICTED = 5

    def label(self) -> str:
        return self.name.replace("_", " ").title()

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# Role access levels (minimum classification a role can access)
# ---------------------------------------------------------------------------

_ROLE_MAX_CLASSIFICATION: dict[str, DataClassification] = {
    "PUBLIC": DataClassification.PUBLIC,
    "CITIZEN": DataClassification.SENSITIVE,        # own data only
    "VERIFIER": DataClassification.CONFIDENTIAL,
    "OFFICER": DataClassification.HIGHLY_SENSITIVE,
    "ADMIN": DataClassification.HIGHLY_SENSITIVE,
    "OPERATOR": DataClassification.RESTRICTED,
    "SYSTEM": DataClassification.RESTRICTED,
}


# ---------------------------------------------------------------------------
# Default field classification policies
# ---------------------------------------------------------------------------

# (resource_type, field_name) → DataClassification
_DEFAULT_POLICIES: dict[tuple[str, str], DataClassification] = {
    # User / Account
    ("user", "id"): DataClassification.INTERNAL,
    ("user", "email"): DataClassification.SENSITIVE,
    ("user", "password_hash"): DataClassification.RESTRICTED,
    ("user", "role"): DataClassification.INTERNAL,
    ("user", "status"): DataClassification.INTERNAL,
    # Document
    ("document", "id"): DataClassification.INTERNAL,
    ("document", "title"): DataClassification.CONFIDENTIAL,
    ("document", "document_type"): DataClassification.CONFIDENTIAL,
    ("document", "verification_status"): DataClassification.CONFIDENTIAL,
    ("document", "storage_key"): DataClassification.HIGHLY_SENSITIVE,
    ("document", "sha256"): DataClassification.SENSITIVE,
    ("document", "raw_content"): DataClassification.HIGHLY_SENSITIVE,
    # Credential
    ("credential", "id"): DataClassification.INTERNAL,
    ("credential", "holder_name"): DataClassification.SENSITIVE,
    ("credential", "passing_year"): DataClassification.CONFIDENTIAL,
    ("credential", "issuer_id"): DataClassification.INTERNAL,
    ("credential", "status"): DataClassification.INTERNAL,
    # Identity claims
    ("claim", "aadhaar"): DataClassification.RESTRICTED,
    ("claim", "pan"): DataClassification.RESTRICTED,
    ("claim", "otp"): DataClassification.RESTRICTED,
    ("claim", "annual_income"): DataClassification.HIGHLY_SENSITIVE,
    ("claim", "address"): DataClassification.HIGHLY_SENSITIVE,
    ("claim", "dob"): DataClassification.SENSITIVE,
    # Keys / Secrets
    ("key", "private_key"): DataClassification.RESTRICTED,
    ("key", "raw_secret"): DataClassification.RESTRICTED,
    ("key", "access_token"): DataClassification.RESTRICTED,
    ("key", "refresh_token"): DataClassification.RESTRICTED,
    # Provider / Integration
    ("provider", "name"): DataClassification.PUBLIC,
    ("provider", "capabilities"): DataClassification.PUBLIC,
    ("provider", "auth_method"): DataClassification.INTERNAL,
    ("provider", "api_secret"): DataClassification.RESTRICTED,
    # Audit events
    ("audit", "event_type"): DataClassification.INTERNAL,
    ("audit", "actor_id"): DataClassification.INTERNAL,
    ("audit", "chain_hash"): DataClassification.INTERNAL,
    # Consent
    ("consent", "decision"): DataClassification.SENSITIVE,
    ("consent", "purpose"): DataClassification.CONFIDENTIAL,
}


# ---------------------------------------------------------------------------
# Classification Policy
# ---------------------------------------------------------------------------


class ClassificationPolicy:
    """Resolves the DataClassification for any (resource_type, field) pair."""

    def __init__(
        self,
        overrides: dict[tuple[str, str], DataClassification] | None = None,
    ) -> None:
        self._policies = dict(_DEFAULT_POLICIES)
        if overrides:
            self._policies.update(overrides)

    def classify(
        self,
        resource_type: str,
        field: str,
        default: DataClassification = DataClassification.CONFIDENTIAL,
    ) -> DataClassification:
        return self._policies.get((resource_type.lower(), field.lower()), default)

    def classify_resource(self, resource_type: str) -> DataClassification:
        """Return the highest classification of any field in a resource type."""
        relevant = [
            v for (rt, _), v in self._policies.items() if rt == resource_type.lower()
        ]
        return max(relevant) if relevant else DataClassification.CONFIDENTIAL


# ---------------------------------------------------------------------------
# Classification Guard
# ---------------------------------------------------------------------------


class ClassificationGuard:
    """Enforces classification-based access and logging rules."""

    def __init__(self, policy: ClassificationPolicy | None = None) -> None:
        self._policy = policy or ClassificationPolicy()

    def assert_loggable(
        self, classification: DataClassification, field: str = ""
    ) -> None:
        """Raise if this classification level must not appear in logs."""
        if classification >= DataClassification.SENSITIVE:
            raise ValueError(
                f"Field '{field}' has classification {classification.label()} "
                f"and MUST NOT appear in logs."
            )

    def is_loggable(self, classification: DataClassification) -> bool:
        return classification < DataClassification.SENSITIVE

    def assert_accessible(
        self, classification: DataClassification, actor_role: str
    ) -> None:
        """Raise if the actor's role cannot access data at this classification level."""
        max_level = _ROLE_MAX_CLASSIFICATION.get(
            actor_role.upper(), DataClassification.PUBLIC
        )
        if classification > max_level:
            raise PermissionError(
                f"Role '{actor_role}' cannot access data classified as "
                f"{classification.label()} (max: {max_level.label()})"
            )

    def can_access(self, classification: DataClassification, actor_role: str) -> bool:
        max_level = _ROLE_MAX_CLASSIFICATION.get(
            actor_role.upper(), DataClassification.PUBLIC
        )
        return classification <= max_level

    def redact(self, value: Any, classification: DataClassification) -> Any:
        """Return redacted sentinel if classification is too sensitive to surface."""
        if classification >= DataClassification.RESTRICTED:
            return "[RESTRICTED]"
        if classification >= DataClassification.HIGHLY_SENSITIVE:
            return "[REDACTED]"
        return value


# ---------------------------------------------------------------------------
# Module singletons
# ---------------------------------------------------------------------------

classification_policy = ClassificationPolicy()
classification_guard = ClassificationGuard(classification_policy)
