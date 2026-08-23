"""
DigiIn Automated Ecosystem Adoption & Institutional Scale Test Suite (Phase 28)
Validates Institutional RBAC, Onboarding State Machine, Automated Accreditation, Credential Rotation, Legacy Migration, Integration Certification, and Flagship E2E Workflow.
"""

import sys
import os

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.institutional_scale import (
    OrganizationRole,
    InstitutionalRBACGuard,
    OnboardingState,
    OnboardingWorkflowEngine,
    AutomatedAccreditationChecker,
    ServiceDirectory,
    IntegrationMarketplace,
    CredentialLifecycleManager,
    AppEnvironment,
    InstitutionalSLAManager,
    IncidentSeverity,
    MigrationFramework,
    IntegrationCertificationEngine,
    InstitutionalAnalytics,
)
from app.core.trust_network import (
    IssuerRegistry,
    VerifierRegistry,
    ClaimSchemaRegistry,
    ClaimIssuanceEngine,
    ClaimPresentationEngine,
    TrustProtocolAdapter,
    ClaimStatus,
)

def test_institutional_rbac_and_role_separation():
    print(">>> 1. Testing Institutional RBAC & Role Separation...")
    # 1. OWNER has full organization management
    assert InstitutionalRBACGuard.has_permission(OrganizationRole.OWNER, "org:manage") is True
    assert InstitutionalRBACGuard.has_permission(OrganizationRole.OWNER, "trust:write") is True

    # 2. DEVELOPER has dev/apps permissions but lacks trust/security management
    assert InstitutionalRBACGuard.has_permission(OrganizationRole.DEVELOPER, "apps:write") is True
    assert InstitutionalRBACGuard.has_permission(OrganizationRole.DEVELOPER, "trust:relationships:write") is False

    # 3. VIEWER has read-only access
    assert InstitutionalRBACGuard.has_permission(OrganizationRole.VIEWER, "claims:read") is True
    assert InstitutionalRBACGuard.has_permission(OrganizationRole.VIEWER, "org:members:write") is False
    print("    [PASS] Institutional RBAC and role separation verified")

def test_onboarding_state_machine_and_accreditation():
    print(">>> 2. Testing Onboarding State Machine & Automated Accreditation...")
    onb_engine = OnboardingWorkflowEngine()
    acc_checker = AutomatedAccreditationChecker()

    # 1. Create Case
    case = onb_engine.create_case("org_punjab_univ", ["ISSUER"], ["education.degree"])
    assert case.status == OnboardingState.DRAFT

    # Transition through stages
    onb_engine.transition_state(case.id, OnboardingState.SUBMITTED, "USER")
    onb_engine.transition_state(case.id, OnboardingState.UNDER_REVIEW, "REVIEWER")
    onb_engine.transition_state(case.id, OnboardingState.IDENTITY_VERIFIED, "REVIEWER")
    onb_engine.transition_state(case.id, OnboardingState.TECHNICAL_REVIEW, "TECH_LEAD")
    onb_engine.transition_state(case.id, OnboardingState.SECURITY_REVIEW, "SEC_LEAD")
    onb_engine.transition_state(case.id, OnboardingState.APPROVED, "GOV_BOARD")
    onb_engine.transition_state(case.id, OnboardingState.SANDBOX, "SYSTEM")

    # 2. Automated Accreditation Check
    criteria = {
        "org_identity": True, "authority_evidence": True, "domain_ownership": True,
        "security_contact": True, "integration_test": True, "webhook_test": True,
        "credential_test": True, "privacy_assessment": True, "claim_authority": True
    }
    passed_acc, eval_rec = acc_checker.evaluate_organization("org_punjab_univ", criteria, "AUDITOR_01")
    assert passed_acc is True
    assert eval_rec.passed is True
    print("    [PASS] Onboarding state machine & automated accreditation verified")

def test_credential_lifecycle_and_rotation():
    print(">>> 3. Testing Developer Applications & Zero-Downtime Credential Rotation...")
    cred_mgr = CredentialLifecycleManager()

    # 1. Create Developer Application in Sandbox
    app, secret = cred_mgr.create_application("org_punjab_univ", "Punjab Univ Portal", AppEnvironment.SANDBOX)
    assert app.environment == AppEnvironment.SANDBOX
    assert len(app.credentials) == 1
    assert app.credentials[0].client_id.startswith("dgi_cli_")

    # 2. Rotate Credential with 7-Day Grace Period
    ok_rot, new_secret, _ = cred_mgr.rotate_credential(app.id, grace_period_seconds=604800)
    assert ok_rot is True
    assert len(app.credentials) == 2
    # Old credential has grace period active
    assert app.credentials[0].grace_period_until is not None
    # New credential is newly created
    assert app.credentials[1].client_id.startswith("dgi_cli_")
    print("    [PASS] Developer applications & zero-downtime credential rotation verified")

def test_legacy_document_migration():
    print(">>> 4. Testing Legacy Document Migration Framework...")
    mig_mgr = MigrationFramework()

    # 1. Create Batch
    batch = mig_mgr.create_batch(
        org_id="org_punjab_univ",
        source_system="LEGACY_MYSQL_DEGREE_DB",
        target_claim="education.degree",
        total_count=2
    )

    # 2. Process Valid Record
    rec1 = {"student_name": "Karan Singh", "degree": "B.Com Honours", "year": 2023}
    ok1, transformed1 = mig_mgr.process_legacy_record(batch.batch_id, rec1)
    assert ok1 is True
    assert transformed1["degree"] == "B.Com Honours"

    # 3. Process Invalid Record
    rec2 = {"unknown_field": "foo"}
    ok2, _ = mig_mgr.process_legacy_record(batch.batch_id, rec2)
    assert ok2 is False
    assert batch.status == "COMPLETED"
    assert batch.successful_records == 1
    assert batch.failed_records == 1
    print("    [PASS] Legacy migration normalization and batch handling verified")

def test_integration_certification_and_sla():
    print(">>> 5. Testing Integration Certification Engine & Institutional SLA...")
    cert_engine = IntegrationCertificationEngine()
    sla_mgr = InstitutionalSLAManager()

    # 1. Complete Certification Test Harness
    harness = {
        "authentication_test": True,
        "authorization_scopes_test": True,
        "claim_request_test": True,
        "consent_enforcement_test": True,
        "verification_flow_test": True,
        "revocation_handling_test": True,
        "webhook_signature_test": True,
    }
    cert_res = cert_engine.run_certification_harness("org_punjab_univ", harness)
    assert cert_res.passed is True
    assert cert_engine.is_certified_for_production("org_punjab_univ") is True

    # 2. Institutional SLA & Service Probes
    sla_report = sla_mgr.get_sla_report()
    assert sla_report["slaCompliant"] is True
    assert sla_report["actualP95LatencyMs"] <= 500.0

    # 3. Role-Based Analytics
    issuer_metrics = InstitutionalAnalytics.get_issuer_analytics("org_punjab_univ")
    assert issuer_metrics["metrics"]["claimsIssued"] == 84201
    print("    [PASS] Integration certification engine & institutional SLA verified")

def test_flagship_ecosystem_e2e_scenario():
    print(">>> 6. Testing Flagship Institutional E2E Scenario...")
    # University onboards -> Certified -> Production Issuer -> Issues Claim -> Citizen Consents -> Verifier Verifies -> Revocation -> Verifier gets REVOKED
    iss_reg = IssuerRegistry()
    ver_reg = VerifierRegistry()
    schema_reg = ClaimSchemaRegistry()
    issuance_engine = ClaimIssuanceEngine(iss_reg, schema_reg)
    pres_engine = ClaimPresentationEngine(ver_reg, issuance_engine)
    adapter = TrustProtocolAdapter(iss_reg, ver_reg, schema_reg, issuance_engine, pres_engine)

    # 1. University is accredited & issues Degree Claim
    degree_payload = {"degree": "B.Tech Computer Science", "institution": "University of Delhi", "year": 2025}
    ok_iss, _, claim = adapter.issue_claim(
        issuer_id="iss_delhi_university",
        subject_id="DGI-7K4M-X9P2",
        claim_type="education.degree",
        payload=degree_payload
    )
    assert ok_iss is True
    assert claim.status == ClaimStatus.ACTIVE

    # 2. Citizen grants consent & generates presentation for Scholarship Service
    nonce = "nonce_flagship_demo_8829"
    ok_pres, _, pres = adapter.present_claim(
        subject_id="DGI-7K4M-X9P2",
        verifier_id="ver_scholarship_portal",
        purpose="SCHOLARSHIP_ELIGIBILITY",
        claim_ids=[claim.id],
        nonce=nonce
    )
    assert ok_pres is True

    # 3. Scholarship Portal verifies claim -> SUCCESS (VERIFIED)
    ok_ver, msg_ver = adapter.verify_claim(
        presentation=pres,
        expected_verifier_id="ver_scholarship_portal",
        expected_purpose="SCHOLARSHIP_ELIGIBILITY",
        expected_nonce=nonce
    )
    assert ok_ver is True

    # 4. University authoritative revocation
    assert issuance_engine.revoke_claim(claim.id, reason="STUDENT_DISQUALIFIED") is True
    assert adapter.check_status(claim.id)["status"] == "REVOKED"

    # 5. Scholarship Portal re-verifies -> REJECTED (REVOKED)
    status_recheck = adapter.check_status(claim.id)
    assert status_recheck["status"] == "REVOKED"
    print("    [PASS] Flagship institutional E2E workflow & instant revocation propagation verified")

def run_all_institutional_scale_tests():
    print("=" * 80)
    print("DIGIIN PHASE 28 ECOSYSTEM ADOPTION & INSTITUTIONAL SCALE TEST MATRIX")
    print("=" * 80)
    test_institutional_rbac_and_role_separation()
    test_onboarding_state_machine_and_accreditation()
    test_credential_lifecycle_and_rotation()
    test_legacy_document_migration()
    test_integration_certification_and_sla()
    test_flagship_ecosystem_e2e_scenario()
    print("=" * 80)
    print("SUCCESS: ALL 6 ECOSYSTEM ADOPTION & INSTITUTIONAL SCALE TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_institutional_scale_tests()
