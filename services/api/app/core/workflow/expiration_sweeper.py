"""
DigiIn Core Workflow Engine — Automated Expiration Sweeper
Periodically identifies and transitions expired documents, consents, requests, and proofs.
"""

import time
from typing import Any


class ExpirationSweeperService:
    @staticmethod
    def sweep_expired_records(
        documents: list[dict[str, Any]],
        consents: list[dict[str, Any]],
        requests: list[dict[str, Any]],
        proofs: list[dict[str, Any]],
        now: float | None = None
    ) -> dict[str, int]:
        """Sweep all domain entity collections and transition expired records to EXPIRED."""
        if now is None:
            now = time.time()

        expired_counts = {
            "documents": 0,
            "consents": 0,
            "requests": 0,
            "proofs": 0
        }

        # 1. Documents
        for doc in documents:
            if doc.get("status") in ("READY", "VERIFIED") and doc.get("expires_at") and now > doc["expires_at"]:
                doc["status"] = "EXPIRED"
                doc["version"] = doc.get("version", 1) + 1
                expired_counts["documents"] += 1

        # 2. Consents
        for cst in consents:
            if cst.get("status") in ("PENDING", "GRANTED") and cst.get("expires_at") and now > cst["expires_at"]:
                cst["status"] = "EXPIRED"
                cst["version"] = cst.get("version", 1) + 1
                expired_counts["consents"] += 1

        # 3. Verification Requests
        for req in requests:
            if req.get("status") in ("DRAFT", "SUBMITTED", "PENDING_CONSENT") and req.get("expires_at") and now > req["expires_at"]:
                req["status"] = "EXPIRED"
                req["version"] = req.get("version", 1) + 1
                expired_counts["requests"] += 1

        # 4. Proofs
        for prf in proofs:
            if prf.get("status") == "ACTIVE" and prf.get("expires_at") and now > prf["expires_at"]:
                prf["status"] = "EXPIRED"
                prf["version"] = prf.get("version", 1) + 1
                expired_counts["proofs"] += 1

        return expired_counts
