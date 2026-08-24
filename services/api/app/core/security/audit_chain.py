"""Phase 8.5 — Tamper-Evident Audit Chain.

Append-only audit event log with SHA-256 hash chaining.

Each event commits to all previous events:

  Event 1: chain_hash = SHA256(event1_canonical)
  Event 2: chain_hash = SHA256(event2_canonical + chain_hash_1)
  Event 3: chain_hash = SHA256(event3_canonical + chain_hash_2)

Therefore modifying any historical event breaks the chain from that point on.

PII rules (strictly enforced):
  - Raw document content MUST NOT appear in any event field
  - OTP values, access tokens, or private keys MUST NOT be logged
  - Aadhaar/PAN numbers MUST NOT appear in event metadata
  - Only opaque IDs and classification-safe fields are stored
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

# PII detection patterns (for guard assertions)
_PII_PATTERNS = [
    re.compile(r"\b[2-9][0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b"),  # Aadhaar
    re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),                  # PAN
    re.compile(r"\b[0-9]{6}\b"),                                 # OTP (6-digit)
    re.compile(r"eyJ[A-Za-z0-9_-]{20,}"),                       # JWT token
    re.compile(r"PRIVATE KEY"),                                   # Private key header
    re.compile(r"BEGIN RSA PRIVATE"),
]


def _contains_pii(text: str) -> bool:
    for pattern in _PII_PATTERNS:
        if pattern.search(text):
            return True
    return False


# ---------------------------------------------------------------------------
# Event types
# ---------------------------------------------------------------------------


class SecurityAuditEventType(StrEnum):
    ACCOUNT_LOGIN = "ACCOUNT_LOGIN"
    ACCOUNT_LOGOUT = "ACCOUNT_LOGOUT"
    ACCOUNT_CREATED = "ACCOUNT_CREATED"
    DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED"
    DOCUMENT_ACCESSED = "DOCUMENT_ACCESSED"
    DOCUMENT_DELETED = "DOCUMENT_DELETED"
    CONSENT_GRANTED = "CONSENT_GRANTED"
    CONSENT_REVOKED = "CONSENT_REVOKED"
    CONSENT_EXPIRED = "CONSENT_EXPIRED"
    PROOF_ISSUED = "PROOF_ISSUED"
    PROOF_VERIFIED = "PROOF_VERIFIED"
    PROOF_TAMPERED = "PROOF_TAMPERED"
    CREDENTIAL_ISSUED = "CREDENTIAL_ISSUED"
    CREDENTIAL_REVOKED = "CREDENTIAL_REVOKED"
    ACCESS_DENIED = "ACCESS_DENIED"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    KEY_ROTATED = "KEY_ROTATED"
    KEY_REVOKED = "KEY_REVOKED"
    DATA_DELETED = "DATA_DELETED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    WEBHOOK_RECEIVED = "WEBHOOK_RECEIVED"
    INTEGRATION_CALL = "INTEGRATION_CALL"
    POLICY_DENIAL = "POLICY_DENIAL"
    NONCE_REPLAYED = "NONCE_REPLAYED"
    CHAIN_INTEGRITY_VERIFIED = "CHAIN_INTEGRITY_VERIFIED"
    CHAIN_INTEGRITY_FAILED = "CHAIN_INTEGRITY_FAILED"


# ---------------------------------------------------------------------------
# Audit Event
# ---------------------------------------------------------------------------


@dataclass
class SecurityAuditEvent:
    event_id: str
    event_type: SecurityAuditEventType
    actor_id: str                    # Opaque user/service ID — never raw name
    resource_type: str
    resource_id: str                 # Opaque resource ID
    purpose: str                     # Why was this access made
    timestamp: datetime
    metadata: dict[str, Any]         # Classification-safe metadata only
    chain_hash: str                  # SHA-256 of (canonical_event + prev_hash)
    prev_hash: str                   # Previous event's chain_hash ("genesis" for first)

    def to_canonical(self) -> str:
        """Deterministic canonical representation for hashing."""
        return json.dumps({
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "actor_id": self.actor_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "purpose": self.purpose,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }, sort_keys=True)

    def to_log_dict(self) -> dict[str, Any]:
        """Safe log representation."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "actor_id": self.actor_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "purpose": self.purpose,
            "timestamp": self.timestamp.isoformat(),
            "chain_hash": self.chain_hash[:16] + "...",  # truncated for brevity
        }


# ---------------------------------------------------------------------------
# Audit Chain
# ---------------------------------------------------------------------------


class AuditChain:
    """
    In-memory append-only audit chain with SHA-256 hash linking.

    Production deployment: persist events to an immutable audit store
    (e.g. AWS CloudTrail, append-only database table, or Merkle tree service).
    """

    GENESIS_HASH = "0" * 64  # Chain anchor

    def __init__(self) -> None:
        self._events: list[SecurityAuditEvent] = []
        self._index: dict[str, int] = {}  # event_id → list index

    def append(
        self,
        event_type: SecurityAuditEventType,
        actor_id: str,
        resource_type: str,
        resource_id: str,
        purpose: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> SecurityAuditEvent:
        """Append a new event to the chain. Returns the committed event."""
        safe_meta = metadata or {}

        # PII guard — raise on accidental PII in metadata
        meta_str = json.dumps(safe_meta, default=str)
        if _contains_pii(meta_str):
            raise ValueError(
                f"PII detected in audit event metadata for event_type={event_type.value}. "
                f"Audit events MUST NOT contain raw PII."
            )

        prev_hash = (
            self._events[-1].chain_hash if self._events else self.GENESIS_HASH
        )

        event_id = f"aev-{uuid.uuid4().hex[:16]}"
        now = datetime.now(UTC)

        # Compute chain hash over canonical event + previous hash
        raw_event = SecurityAuditEvent(
            event_id=event_id,
            event_type=event_type,
            actor_id=actor_id,
            resource_type=resource_type,
            resource_id=resource_id,
            purpose=purpose,
            timestamp=now,
            metadata=safe_meta,
            chain_hash="",      # placeholder
            prev_hash=prev_hash,
        )
        canonical = raw_event.to_canonical() + prev_hash
        chain_hash = hashlib.sha256(canonical.encode()).hexdigest()
        raw_event.chain_hash = chain_hash

        idx = len(self._events)
        self._events.append(raw_event)
        self._index[event_id] = idx

        return raw_event

    def verify_integrity(self, from_index: int = 0) -> tuple[bool, str]:
        """
        Replay the chain from from_index and verify all hashes are consistent.

        Returns (is_valid, reason).
        If any event was modified, is_valid=False and reason names the broken event.
        """
        self.GENESIS_HASH if from_index == 0 else self._events[from_index - 1].chain_hash

        for i in range(from_index, len(self._events)):
            event = self._events[i]
            canonical = event.to_canonical() + (
                self.GENESIS_HASH if i == 0 else self._events[i - 1].chain_hash
            )
            expected = hashlib.sha256(canonical.encode()).hexdigest()
            if expected != event.chain_hash:
                return False, f"Chain broken at event {i} (id={event.event_id})"

        return True, f"Chain intact: {len(self._events) - from_index} events verified"

    def get_events(
        self,
        event_type: SecurityAuditEventType | None = None,
        actor_id: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Return safe log dicts (never raw PII) filtered by type/actor."""
        results = self._events
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        if actor_id:
            results = [e for e in results if e.actor_id == actor_id]
        return [e.to_log_dict() for e in results[-limit:]]

    def count(self) -> int:
        return len(self._events)

    def tail(self, n: int = 10) -> list[dict[str, Any]]:
        return [e.to_log_dict() for e in self._events[-n:]]


# ---------------------------------------------------------------------------
# Module singleton
# ---------------------------------------------------------------------------

audit_chain = AuditChain()
