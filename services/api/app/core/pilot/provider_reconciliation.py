"""
DigiIn Controlled Pilot & Production Validation — Provider Transaction Reconciliation
Matches internal DigiIn verification records against external provider transaction logs, detecting discrepancies and state mismatches.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProviderTransactionRecord:
    provider_transaction_id: str
    provider_id: str
    verification_id: str
    status: str
    timestamp: float = field(default_factory=time.time)

@dataclass
class ReconciliationResult:
    reconciliation_id: str
    matched_count: int
    mismatches: list[dict[str, Any]]
    status: str
    executed_at: float = field(default_factory=time.time)

class ProviderReconciliationEngine:
    def __init__(self):
        self._provider_transactions: dict[str, ProviderTransactionRecord] = {}

    def record_provider_transaction(
        self,
        provider_id: str,
        verification_id: str,
        provider_txn_id: str,
        status: str
    ) -> ProviderTransactionRecord:
        rec = ProviderTransactionRecord(
            provider_transaction_id=provider_txn_id,
            provider_id=provider_id,
            verification_id=verification_id,
            status=status
        )
        self._provider_transactions[verification_id] = rec
        return rec

    def reconcile_batch(
        self,
        digiin_verifications: list[dict[str, Any]]
    ) -> ReconciliationResult:
        recon_id = f"rcn_{secrets.token_hex(8)}"
        matched = 0
        mismatches = []

        for v in digiin_verifications:
            v_id = v.get("id", "")
            dgi_status = v.get("status", "")
            provider_rec = self._provider_transactions.get(v_id)

            if not provider_rec:
                mismatches.append({
                    "verificationId": v_id,
                    "reason": "MISSING_IN_PROVIDER_TRANSACTIONS",
                    "digiinStatus": dgi_status,
                    "providerStatus": None
                })
            elif provider_rec.status != dgi_status:
                mismatches.append({
                    "verificationId": v_id,
                    "reason": "STATE_MISMATCH",
                    "digiinStatus": dgi_status,
                    "providerStatus": provider_rec.status,
                    "providerTxnId": provider_rec.provider_transaction_id
                })
            else:
                matched += 1

        status = "HEALTHY" if not mismatches else "DISCREPANCIES_DETECTED"
        return ReconciliationResult(
            reconciliation_id=recon_id,
            matched_count=matched,
            mismatches=mismatches,
            status=status
        )
