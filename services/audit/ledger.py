"""Sovereign Immutable Audit Ledger with Cryptographic Hash Chaining."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any


class AuditBlock:
    """A tamper-evident cryptographic audit record block."""

    def __init__(
        self,
        index: int,
        event_type: str,
        aggregate_id: str,
        actor: str,
        message: str,
        previous_hash: str,
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.index = index
        self.event_type = event_type
        self.aggregate_id = aggregate_id
        self.actor = actor
        self.message = message
        self.previous_hash = previous_hash
        self.timestamp = timestamp or datetime.now(UTC).isoformat()
        self.metadata = metadata or {}
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        """Compute SHA-256 digest of block contents."""
        block_data = {
            "index": self.index,
            "eventType": self.event_type,
            "aggregateId": self.aggregate_id,
            "actor": self.actor,
            "message": self.message,
            "previousHash": self.previous_hash,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
        raw_json = json.dumps(block_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw_json.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "eventType": self.event_type,
            "aggregateId": self.aggregate_id,
            "actor": self.actor,
            "message": self.message,
            "previousHash": self.previous_hash,
            "hash": self.hash,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class SovereignAuditLedger:
    """Manages append-only immutable audit block chain."""

    def __init__(self) -> None:
        self.chain: list[AuditBlock] = []
        self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        genesis = AuditBlock(
            index=0,
            event_type="GENESIS_SOVEREIGN_ROOT",
            aggregate_id="platform_root_genesis",
            actor="SYSTEM_ROOT",
            message="DigiLocker X Sovereign Cryptographic Audit Genesis Initialized.",
            previous_hash="0" * 64,
            timestamp="2026-08-22T00:00:00Z",
            metadata={"version": "1.0.0", "algorithm": "SHA-256"},
        )
        self.chain.append(genesis)

    def append_event(
        self,
        event_type: str,
        aggregate_id: str,
        actor: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> AuditBlock:
        """Appends a new verified event block chained to the previous block hash."""
        prev_block = self.chain[-1]
        new_block = AuditBlock(
            index=len(self.chain),
            event_type=event_type,
            aggregate_id=aggregate_id,
            actor=actor,
            message=message,
            previous_hash=prev_block.hash,
            metadata=metadata,
        )
        self.chain.append(new_block)
        return new_block

    def verify_chain_integrity(self) -> tuple[bool, str | None]:
        """Validates the entire ledger's cryptographic hash continuity."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            if current.previous_hash != prev.hash:
                return False, f"Broken chain link at index {i}: previousHash mismatch."

            recomputed_hash = current.compute_hash()
            if current.hash != recomputed_hash:
                return False, f"Tampered block detected at index {i}: hash mismatch."

        return True, None

    def query_events(
        self,
        event_type: str | None = None,
        aggregate_id: str | None = None,
        actor: str | None = None,
    ) -> list[dict[str, Any]]:
        """Filter audit events matching criteria."""
        results = []
        for block in self.chain:
            if event_type and block.event_type != event_type:
                continue
            if aggregate_id and block.aggregate_id != aggregate_id:
                continue
            if actor and block.actor != actor:
                continue
            results.append(block.to_dict())
        return results


audit_ledger = SovereignAuditLedger()
