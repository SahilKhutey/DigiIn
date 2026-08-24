"""Deterministic Demo Seed & One-Click Reset Subsystem.

Provides pre-seeded, deterministic sandbox fixtures for live hackathon jury demonstrations.
Enables instant 1-click state reset for repeatable live reviews.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from app.core.proofs import (
    KeyManager,
    ProofSigningService,
    ProofVerifier,
    TrustedIssuer,
    TrustRegistry,
)
from app.core.public_service.service_registry import (
    ApplicationStatus,
    ServiceApplication,
    service_registry,
)


@dataclass
class DemoSeedState:
    citizen_account_id: str
    citizen_name: str
    service_id: str
    service_name: str
    organization_id: str
    organization_name: str
    valid_proof_id: str
    tampered_proof_id: str
    expired_proof_id: str
    revoked_proof_id: str
    credentials: list[dict[str, Any]]


class DemoSeedManager:
    """Manages deterministic demo fixtures and 1-click reset."""

    def __init__(self) -> None:
        self._key_manager = KeyManager()
        self._key_manager.generate_and_register_key("KEY-DEMO-ROOT")
        self._trust_registry = TrustRegistry()
        self._trust_registry.register_issuer(
            TrustedIssuer(
                id="iss_digiin_demo_authority",
                name="DigiIn Verified Demo Authority",
                issuer_identifier="did:digiin:authority:demo",
                trusted_proof_types=["SCHOLARSHIP_ELIGIBILITY_VERIFIED"],
                status="ACTIVE",
            )
        )
        self._signer = ProofSigningService(self._key_manager)
        self._verifier = ProofVerifier(self._key_manager, self._trust_registry)

    def get_seed_state(self) -> DemoSeedState:
        return DemoSeedState(
            citizen_account_id="DIN-DEMO-001",
            citizen_name="Demo Citizen (Rahul Sharma)",
            service_id="srv_scholarship_du",
            service_name="National Merit-cum-Means Scholarship",
            organization_id="ORG-DEMO-001",
            organization_name="University Scholarship Service",
            valid_proof_id="PRF-DEMO-1042",
            tampered_proof_id="PRF-TAMPERED-01",
            expired_proof_id="PRF-EXPIRED-01",
            revoked_proof_id="PRF-REVOKED-01",
            credentials=[
                {
                    "type": "IDENTITY",
                    "title": "Sovereign Identity Assertion",
                    "issuer": "DigiIn Verified Demo Authority",
                    "status": "Verified Active",
                    "verified_date": "24 Aug 2026",
                },
                {
                    "type": "DOMICILE",
                    "title": "State of Chhattisgarh Domicile",
                    "issuer": "State Revenue Department",
                    "status": "Verified Active",
                    "verified_date": "24 Aug 2026",
                },
                {
                    "type": "INCOME",
                    "title": "Income Eligibility (< 2.5L Threshold)",
                    "issuer": "Revenue & Tax Assessment Authority",
                    "status": "Verified Active",
                    "verified_date": "24 Aug 2026",
                },
                {
                    "type": "EDUCATION",
                    "title": "CBSE Higher Secondary Class XII Marksheet (94.2%)",
                    "issuer": "Central Board of Secondary Education",
                    "status": "Verified Active",
                    "verified_date": "24 Aug 2026",
                },
            ],
        )

    def reset_demo(self) -> dict[str, Any]:
        """Resets all public service applications and re-seeds deterministic baseline demo state."""
        state = self.get_seed_state()

        # Reset application in registry
        app = ServiceApplication(
            application_id="DGI-SCH-2026-1042",
            service_id=state.service_id,
            service_name=state.service_name,
            citizen_account_id=state.citizen_account_id,
            citizen_name=state.citizen_name,
            status=ApplicationStatus.SUBMITTED,
            created_at=time.time() - 120,
            updated_at=time.time(),
            disclosed_claims={
                "fullName": state.citizen_name,
                "domicileState": "Chhattisgarh",
                "incomeEligibility": True,
                "academicScore": "CBSE Class XII (94.2%)",
            },
            withheld_claims=[
                "Aadhaar Number (Redacted)",
                "Raw Marksheet PDF Files (0 Bytes Transferred)",
                "Exact Tax Figures",
                "Full Residential Address",
            ],
            proof_id=state.valid_proof_id,
            institution_verification_result={
                "verified": True,
                "signature_valid": True,
                "issuer_trusted": True,
                "verified_at": time.time(),
                "verdict": "VERIFIED_ELIGIBLE",
            },
        )
        service_registry.update_application(app)

        return {
            "status": "success",
            "message": "Deterministic demo environment reset in 1-click.",
            "citizen_account_id": state.citizen_account_id,
            "application_id": app.application_id,
            "proof_id": state.valid_proof_id,
            "credentials_count": len(state.credentials),
        }


demo_seed_manager = DemoSeedManager()
