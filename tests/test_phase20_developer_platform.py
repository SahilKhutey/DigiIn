"""
DigiIn Automated Developer & API Platform Test Suite (Phase 20)
Validates Developer Organizations, Applications, OAuth token issuance, DigiIn Account ID resolution, consent delegation, proof verification, webhooks, and multi-tenant isolation.
"""

import sys
import os
import time

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.developer_platform import (
    OAuthAuthorizationServer,
    AccountIdResolver,
    WebhookDispatcher,
    UsageMeterService,
    DeveloperGateway,
    MultiTenantIsolationError,
)

def test_complete_developer_verification_lifecycle():
    print(">>> 1. Testing Complete 20-Step Developer Verification Lifecycle...")
    auth_server = OAuthAuthorizationServer()
    account_resolver = AccountIdResolver()
    webhook_dispatcher = WebhookDispatcher()
    usage_meter = UsageMeterService()

    gateway = DeveloperGateway(auth_server, account_resolver, webhook_dispatcher, usage_meter)

    # 1. Register Developer Organization
    org = auth_server.register_organization(name="IIT Delhi Admissions Department", org_type="UNIVERSITY")
    assert org.id.startswith("org_")

    # 2. Register Developer Application
    app, secret = auth_server.register_application(
        organization_id=org.id,
        name="IITD PG Admissions Portal",
        scopes=["verification:create", "verification:read", "verification:education", "proof:verify", "proof:read", "subject:resolve"],
        environment="PRODUCTION"
    )
    assert app.client_id.startswith("dgi_client_")

    # 3. Register Webhook Subscription
    sub = webhook_dispatcher.register_subscription(
        application_id=app.id,
        target_url="https://admissions.iitd.ac.in/api/digiin-webhook",
        events=["verification.completed", "proof.issued"]
    )
    assert sub.id.startswith("sub_")

    # 4. Request OAuth Access Token
    success, err, token_data = auth_server.issue_client_credentials_token(
        client_id=app.client_id,
        client_secret=secret,
        requested_scopes=["verification:create", "proof:read", "verification:education"]
    )
    assert success is True, f"Token issue failed: {err}"
    token_str = token_data["access_token"]

    # 5. Submit DigiIn Account ID for verification
    account_id = "DGI-SBX-001"
    ok, err, verif_res = gateway.create_verification_request(
        token_str=token_str,
        account_id=account_id,
        claim_types=["EDUCATION"],
        purpose="POSTGRADUATE_ADMISSION"
    )
    assert ok is True, f"Verification create failed: {err}"
    verif_id = verif_res["verificationId"]
    assert verif_res["status"] == "CONSENT_REQUIRED"

    # 6. Citizen reviews & grants consent
    ok, err, grant_res = gateway.citizen_grant_consent(verif_id, approved=True)
    assert ok is True, f"Consent grant failed: {err}"
    assert grant_res["status"] == "VERIFIED"
    proof_id = grant_res["proofId"]
    assert proof_id.startswith("prf_")

    # 7. Check Webhook Dispatch
    assert len(webhook_dispatcher._delivery_history) > 0
    webhook_event = webhook_dispatcher._delivery_history[-1]
    assert webhook_event["eventType"] == "verification.completed"
    assert webhook_event["payload"]["proofId"] == proof_id
    assert "X-DigiIn-Signature" in webhook_event["headers"]

    # 8. External Application retrieves proof
    ok, err, proof_obj = gateway.retrieve_proof(token_str=token_str, proof_id=proof_id)
    assert ok is True, f"Proof retrieval failed: {err}"
    assert proof_obj["proofId"] == proof_id
    assert proof_obj["status"] == "ACTIVE"

    # 9. External Application independently verifies cryptographic proof
    outcome = gateway.proof_verifier.verify(proof_obj, expected_purpose="POSTGRADUATE_ADMISSION")
    assert outcome.valid is True
    assert outcome.signature_valid is True
    assert outcome.issuer_trusted is True

    # 10. Citizen revokes consent -> Proof access is blocked
    verif_record = gateway._verifications[verif_id]
    consent_id = verif_record["consentId"]
    gateway.revoke_citizen_consent(consent_id)

    ok_revoked, err_revoked, _ = gateway.retrieve_proof(token_str=token_str, proof_id=proof_id)
    assert ok_revoked is False
    assert "CONSENT_REVOKED" in err_revoked
    print("    [PASS] 20-step verification delegation, proof minting & revocation verified")

def test_multi_tenant_isolation_boundary():
    print(">>> 2. Testing Multi-Tenant Isolation Boundary Defense...")
    auth_server = OAuthAuthorizationServer()
    account_resolver = AccountIdResolver()
    webhook_dispatcher = WebhookDispatcher()
    usage_meter = UsageMeterService()
    gateway = DeveloperGateway(auth_server, account_resolver, webhook_dispatcher, usage_meter)

    # Org A (University of Delhi)
    org_a = auth_server.register_organization("University of Delhi", "UNIVERSITY")
    app_a, secret_a = auth_server.register_application(org_a.id, "DU Portal", ["verification:create", "proof:read"])
    _, _, tok_data_a = auth_server.issue_client_credentials_token(app_a.client_id, secret_a)

    # Org B (Ministry of External Affairs)
    org_b = auth_server.register_organization("Ministry of External Affairs", "GOVERNMENT")
    app_b, secret_b = auth_server.register_application(org_b.id, "MEA Portal", ["verification:create", "proof:read"])
    _, _, tok_data_b = auth_server.issue_client_credentials_token(app_b.client_id, secret_b)

    # Org A initiates verification & obtains proof
    _, _, verif_res = gateway.create_verification_request(tok_data_a["access_token"], "DGI-SBX-001", ["EDUCATION"], "DU_ADMISSION")
    _, _, grant_res = gateway.citizen_grant_consent(verif_res["verificationId"], approved=True)
    proof_id_a = grant_res["proofId"]

    # Org B attempts to access Org A's proof with Org B's token -> MUST FAIL (Isolation Violation)
    try:
        ok, err, _ = gateway.retrieve_proof(tok_data_b["access_token"], proof_id_a)
        assert False, "Multi-tenant violation: Org B successfully accessed Org A's proof!"
    except MultiTenantIsolationError as ex:
        assert "TENANT_ISOLATION_VIOLATION" in str(ex)
    print("    [PASS] Cross-organization multi-tenant isolation enforced")

def test_scope_enforcement_and_anti_enumeration():
    print(">>> 3. Testing Granular Scope Enforcement & Anti-Enumeration...")
    auth_server = OAuthAuthorizationServer()
    account_resolver = AccountIdResolver()
    webhook_dispatcher = WebhookDispatcher()
    usage_meter = UsageMeterService()
    gateway = DeveloperGateway(auth_server, account_resolver, webhook_dispatcher, usage_meter)

    # Application with ONLY proof:verify scope (no verification:create scope)
    org = auth_server.register_organization("Verifier Org", "ENTERPRISE")
    app, secret = auth_server.register_application(org.id, "Read Only Verifier", ["proof:verify"])
    _, _, tok_data = auth_server.issue_client_credentials_token(app.client_id, secret, requested_scopes=["proof:verify"])

    # Attempt to create verification without verification:create scope -> FAIL
    ok, err, _ = gateway.create_verification_request(tok_data["access_token"], "DGI-SBX-001", ["EDUCATION"], "CHECK")
    assert ok is False
    assert "INSUFFICIENT_SCOPE" in err

    # Anti-enumeration test: 10 consecutive invalid Account ID lookups
    client_ip = "192.168.1.105"
    for i in range(10):
        ok, err, _ = account_resolver.resolve_account_id(f"DGI-FAKE-ENUM-{i}", client_ip=client_ip)
        assert ok is False
        assert "SUBJECT_NOT_FOUND" in err

    # 11th lookup is throttled with RATE_LIMITED
    ok_11, err_11, _ = account_resolver.resolve_account_id("DGI-FAKE-ENUM-11", client_ip=client_ip)
    assert ok_11 is False
    assert "RATE_LIMITED" in err_11
    print("    [PASS] Granular scope validation & anti-enumeration defense verified")

def run_all_developer_platform_tests():
    print("=" * 80)
    print("DIGIIN PHASE 20 DEVELOPER & API PLATFORM TEST MATRIX")
    print("=" * 80)
    test_complete_developer_verification_lifecycle()
    test_multi_tenant_isolation_boundary()
    test_scope_enforcement_and_anti_enumeration()
    print("=" * 80)
    print("SUCCESS: ALL 3 DEVELOPER & API PLATFORM TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_developer_platform_tests()
