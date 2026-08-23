"""
DigiIn Developer Platform — Developer Gateway
Facade orchestrating external verification requests, citizen consent grants, provider execution, proof minting, and proof retrieval.
"""

from __future__ import annotations

import secrets
import time
from typing import Any

from app.core.proofs import (
    KeyManager,
    ProofSigningService,
    ProofVerifier,
    TrustRegistry,
    VerifiedClaim,
)
from app.core.providers import CoreProviderRegistry, ProviderGateway

from .account_id_resolver import AccountIdResolver
from .models import ConsentGrant
from .multi_tenant_guard import MultiTenantGuard
from .oauth_server import OAuthAuthorizationServer
from .usage_meter import UsageMeterService
from .webhook_dispatcher import WebhookDispatcher


class DeveloperGateway:
    def __init__(
        self,
        auth_server: OAuthAuthorizationServer,
        account_resolver: AccountIdResolver,
        webhook_dispatcher: WebhookDispatcher,
        usage_meter: UsageMeterService
    ):
        self.auth_server = auth_server
        self.account_resolver = account_resolver
        self.webhook_dispatcher = webhook_dispatcher
        self.usage_meter = usage_meter

        # Core provider and proof services
        self.provider_registry = CoreProviderRegistry()
        self.provider_gateway = ProviderGateway(self.provider_registry)
        self.key_manager = KeyManager()
        self.key_manager.generate_and_register_key("KEY-DEV-2026-PRIMARY")
        self.trust_registry = TrustRegistry()
        self.proof_signer = ProofSigningService(self.key_manager)
        self.proof_verifier = ProofVerifier(self.key_manager, self.trust_registry)

        self._verifications: dict[str, dict[str, Any]] = {}
        self._consents: dict[str, ConsentGrant] = {}
        self._proofs: dict[str, dict[str, Any]] = {}

    def create_verification_request(
        self,
        token_str: str,
        account_id: str,
        claim_types: list[str],
        purpose: str,
        client_ip: str = "127.0.0.1"
    ) -> tuple[bool, str | None, dict[str, Any] | None]:
        """
        External API entry point: POST /v1/verifications
        Validates token, resolves Account ID, checks scopes, creates verification request with CONSENT_REQUIRED.
        """
        introspection = self.auth_server.introspect_token(token_str)
        if not introspection.get("active"):
            return False, f"UNAUTHORIZED: Token invalid or expired ({introspection.get('reason')}).", None

        app_id = introspection.get("app_id") or introspection.get("sub") or introspection.get("client_id")
        app_scopes = introspection.get("scopes", [])

        # Validate required scope
        if "verification:create" not in app_scopes:
            return False, "INSUFFICIENT_SCOPE: Token missing 'verification:create' scope.", None

        # Resolve Account ID
        ok, err, subject_ref = self.account_resolver.resolve_account_id(account_id, client_ip=client_ip)
        if not ok:
            return False, err, None

        verif_id = f"ver_{secrets.token_hex(10)}"
        now = time.time()
        record = {
            "id": verif_id,
            "applicationId": app_id,
            "organizationId": introspection.get("organization_id"),
            "subjectReference": subject_ref,
            "accountId": account_id,
            "claims": claim_types,
            "purpose": purpose,
            "status": "CONSENT_REQUIRED",
            "proofId": None,
            "createdAt": now,
            "updatedAt": now,
        }
        self._verifications[verif_id] = record
        return True, None, {
            "verificationId": verif_id,
            "status": "CONSENT_REQUIRED",
            "message": "Verification request created. Awaiting citizen consent approval.",
            "consentUrl": f"https://app.digiin.in/consent/verify/{verif_id}",
        }

    def citizen_grant_consent(
        self,
        verification_id: str,
        approved: bool = True
    ) -> tuple[bool, str | None, dict[str, Any] | None]:
        """
        Citizen consent flow: Citizen reviews purpose and authorizes provider verification.
        Executes provider evidence retrieval, normalizes evidence, mints Ed25519 proof, and delivers webhook.
        """
        record = self._verifications.get(verification_id)
        if not record:
            return False, "VERIFICATION_NOT_FOUND", None

        if not approved:
            record["status"] = "CONSENT_REJECTED"
            record["updatedAt"] = time.time()
            return True, None, {"status": "CONSENT_REJECTED"}

        # Record Consent Grant
        consent_id = f"cst_{secrets.token_hex(10)}"
        grant = ConsentGrant(
            id=consent_id,
            subject_id=record["subjectReference"],
            application_id=record["applicationId"],
            claims=record["claims"],
            purpose=record["purpose"],
            status="GRANTED"
        )
        self._consents[consent_id] = grant
        record["consentId"] = consent_id
        record["status"] = "PROCESSING"

        # 1. Execute Provider Verification
        verified_claims_list = []
        for claim_type in record["claims"]:
            ok, err, evidence = self.provider_gateway.execute_verification(
                claim_type=claim_type,
                subject_ref=record["subjectReference"],
                purpose=record["purpose"],
                request_id=verification_id
            )
            if ok and evidence:
                verified_claims_list.append(
                    VerifiedClaim(
                        type=claim_type,
                        value=evidence.value,
                        status="VERIFIED",
                        source_id=evidence.provider_id,
                        verification_id=verification_id
                    )
                )

        if not verified_claims_list:
            record["status"] = "VERIFICATION_FAILED"
            return False, "PROVIDER_FAILED: Could not obtain verified evidence from authoritative sources.", None

        # 2. Mint Signed Proof Object
        signed_proof = self.proof_signer.mint_signed_proof(
            subject_id=record["subjectReference"],
            claims=verified_claims_list,
            purpose=record["purpose"],
            proof_type="EDUCATION_VERIFIED" if "EDUCATION" in record["claims"] else "IDENTITY_VERIFIED"
        )
        proof_id = signed_proof["proofId"]
        self._proofs[proof_id] = {
            "proof": signed_proof,
            "applicationId": record["applicationId"],
            "organizationId": record["organizationId"],
            "consentId": consent_id,
        }

        # 3. Update Verification Record
        record["status"] = "VERIFIED"
        record["proofId"] = proof_id
        record["updatedAt"] = time.time()

        # 4. Dispatch Webhook Event to External Application
        self.webhook_dispatcher.dispatch_event(
            event_type="verification.completed",
            application_id=record["applicationId"],
            payload={
                "verificationId": verification_id,
                "status": "VERIFIED",
                "proofId": proof_id,
                "purpose": record["purpose"],
                "claims": record["claims"],
            }
        )

        return True, None, {
            "verificationId": verification_id,
            "status": "VERIFIED",
            "proofId": proof_id,
        }

    def retrieve_proof(
        self,
        token_str: str,
        proof_id: str
    ) -> tuple[bool, str | None, dict[str, Any] | None]:
        """External API endpoint: GET /v1/proofs/:id with multi-tenant isolation and scope checking."""
        introspection = self.auth_server.introspect_token(token_str)
        if not introspection.get("active"):
            return False, f"UNAUTHORIZED: Token invalid or expired ({introspection.get('reason')}).", None

        scopes = introspection.get("scopes", [])
        if "proof:read" not in scopes:
            return False, "INSUFFICIENT_SCOPE: Token missing 'proof:read' scope.", None

        entry = self._proofs.get(proof_id)
        if not entry:
            return False, "PROOF_NOT_FOUND: Verifiable proof does not exist.", None

        # Multi-tenant isolation guard
        caller_org_id = introspection.get("organization_id")
        MultiTenantGuard.enforce_resource_ownership(entry["organizationId"], caller_org_id)

        # Check if consent was revoked
        consent_id = entry.get("consentId")
        if consent_id and consent_id in self._consents:
            cst = self._consents[consent_id]
            if cst.status == "REVOKED":
                return False, "CONSENT_REVOKED: Citizen has revoked consent for this proof.", None

        return True, None, entry["proof"]

    def revoke_citizen_consent(self, consent_id: str) -> bool:
        """Citizen revokes previously granted consent."""
        grant = self._consents.get(consent_id)
        if grant:
            grant.status = "REVOKED"
            grant.revoked_at = time.time()
            # Invalidate any associated proof status
            for p_entry in self._proofs.values():
                if p_entry.get("consentId") == consent_id:
                    p_entry["proof"]["status"] = "REVOKED"
            return True
        return False
