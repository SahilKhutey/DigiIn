"""
DigiIn Automated Controlled Pilot & Production Validation Test Suite (Phase 25)
Validates Pilot Governance, Organization Onboarding Checklist, Provider Reconciliation, Proof Revocation, Support Operations, Risk Register, User Feedback, and Go/No-Go Gate.
"""

import sys
import os

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.pilot import (
    PilotGovernanceManager,
    OrganizationOnboardingWorkflow,
    ProviderReconciliationEngine,
    SupportOperationsService,
    PilotRiskRegister,
    UserFeedbackCollector,
    ProductionGoNoGoGate,
    TrafficRampStage,
    PilotDashboardService,
)
from app.core.proofs import KeyManager, TrustRegistry, ProofSigningService, ProofVerifier, VerifiedClaim

def test_pilot_governance_and_boundary_enforcement():
    print(">>> 1. Testing Pilot Program Governance & Boundary Scoping...")
    gov = PilotGovernanceManager()
    pid = "pilot_digiin_2026_q3"

    # 1. Enrolled organization and document type -> ALLOW
    ok, err = gov.validate_pilot_boundary(
        program_id=pid,
        organization_id="org_delhi_university",
        document_type="DEGREE_CERTIFICATE",
        provider_id="mock-cbse-001"
    )
    assert ok is True

    # 2. Unregistered organization -> REJECT (ORGANIZATION_OUTSIDE_PILOT)
    ok_unauth_org, err_unauth_org = gov.validate_pilot_boundary(
        program_id=pid,
        organization_id="org_unknown_unregistered",
        document_type="DEGREE_CERTIFICATE",
        provider_id="mock-cbse-001"
    )
    assert ok_unauth_org is False
    assert "ORGANIZATION_OUTSIDE_PILOT" in err_unauth_org

    # 3. Unsupported document type -> REJECT (DOCUMENT_TYPE_OUTSIDE_PILOT)
    ok_bad_doc, err_bad_doc = gov.validate_pilot_boundary(
        program_id=pid,
        organization_id="org_delhi_university",
        document_type="UNREGISTERED_PASSPORT",
        provider_id="mock-cbse-001"
    )
    assert ok_bad_doc is False
    assert "DOCUMENT_TYPE_OUTSIDE_PILOT" in err_bad_doc
    print("    [PASS] Pilot boundary scoping & restriction verified")

def test_organization_onboarding_checklist():
    print(">>> 2. Testing Organization Onboarding & 8-Point Activation Checklist...")
    workflow = OrganizationOnboardingWorkflow()

    # 1. Register new organization
    org = workflow.register_organization(
        org_id="org_iit_delhi",
        legal_name="Indian Institute of Technology Delhi",
        display_name="IIT Delhi",
        admin_id="adm_sharma_01",
        allowed_types=["DEGREE_CERTIFICATE"],
        allowed_scopes=["education:degree"]
    )
    assert org.status == "PENDING"

    # 2. Attempt activation with incomplete checklist -> REJECT
    ok_early, msg_early, _ = workflow.activate_organization("org_iit_delhi")
    assert ok_early is False
    assert "INCOMPLETE_ONBOARDING_CHECKLIST" in msg_early

    # 3. Complete all 8 mandatory checklist items
    items = [
        "identity_verified", "admin_verified", "scopes_approved",
        "provider_access_configured", "callback_urls_configured",
        "security_contact_registered", "privacy_contact_registered",
        "test_verification_completed"
    ]
    for item in items:
        workflow.complete_checklist_item("org_iit_delhi", item)

    # 4. Activate organization -> SUCCESS
    ok_active, msg_active, active_org = workflow.activate_organization("org_iit_delhi")
    assert ok_active is True
    assert active_org.status == "ACTIVE"
    assert active_org.activated_at is not None
    print("    [PASS] Organization 8-point onboarding checklist & activation verified")

def test_provider_transaction_reconciliation():
    print(">>> 3. Testing Provider Transaction Reconciliation Engine...")
    recon_engine = ProviderReconciliationEngine()

    # Seed provider transactions
    recon_engine.record_provider_transaction("cbse-01", "vreq_001", "txn_cbse_9981", "VERIFIED")
    recon_engine.record_provider_transaction("cbse-01", "vreq_002", "txn_cbse_9982", "REJECTED")

    # Reconciliation batch with 1 matching, 1 state mismatch, 1 missing in provider
    digiin_batch = [
        {"id": "vreq_001", "status": "VERIFIED"},   # MATCH
        {"id": "vreq_002", "status": "VERIFIED"},   # STATE MISMATCH (Provider has REJECTED)
        {"id": "vreq_003", "status": "VERIFIED"},   # MISSING IN PROVIDER
    ]

    result = recon_engine.reconcile_batch(digiin_batch)
    assert result.matched_count == 1
    assert len(result.mismatches) == 2
    assert result.status == "DISCREPANCIES_DETECTED"
    print("    [PASS] Provider transaction reconciliation & discrepancy detection verified")

def test_end_to_end_proof_verification_and_revocation():
    print(">>> 4. Testing End-to-End Proof Verification & Revocation...")
    key_mgr = KeyManager()
    trust_reg = TrustRegistry()
    key_mgr.generate_and_register_key("KEY-PILOT-2026")

    signer = ProofSigningService(key_mgr)
    verifier = ProofVerifier(key_mgr, trust_reg)

    # 1. Mint proof
    proof = signer.mint_signed_proof(
        subject_id="subj_citizen_pilot_01",
        claims=[VerifiedClaim(type="DEGREE", value={"title": "B.Sc Computer Science"})],
        purpose="PILOT_ADMISSION_VERIFICATION"
    )

    # 2. Verify proof -> VALID
    res_valid = verifier.verify(proof, expected_purpose="PILOT_ADMISSION_VERIFICATION")
    assert res_valid.valid is True
    assert res_valid.signature_valid is True

    # 3. Revoke proof
    proof["status"] = "REVOKED"
    proof["revokedAt"] = 1771800000.0

    # 4. Verifier re-checks revoked proof -> REJECT (status_valid is False)
    res_revoked = verifier.verify(proof, expected_purpose="PILOT_ADMISSION_VERIFICATION")
    assert res_revoked.valid is False
    assert res_revoked.status_valid is False
    assert "REVOKED" in (res_revoked.reason or "")
    print("    [PASS] E2E proof issuance, verification & revocation propagation verified")

def test_support_operations_and_risk_register():
    print(">>> 5. Testing Support Operations & Risk Register...")
    support = SupportOperationsService()
    risks = PilotRiskRegister()

    # 1. Support ticket lifecycle
    tkt = support.create_ticket(
        requester_id="org_delhi_univ",
        category="VERIFICATION",
        subject="CBSE Callback Latency",
        description="Experiencing 3s delay on batch verification",
        priority="HIGH"
    )
    assert tkt.status == "OPEN"

    # Escalate ticket to engineering
    ok_esc, esc_tkt = support.escalate_ticket(tkt.id, "TIER_3_ENGINEERING", "Provider timeout surge", actor="support_lead")
    assert ok_esc is True
    assert esc_tkt.assigned_tier == "TIER_3_ENGINEERING"

    # Resolve ticket
    ok_res, res_tkt = support.resolve_ticket(tkt.id, "Circuit breaker threshold tuned", actor="eng_lead")
    assert ok_res is True
    assert res_tkt.status == "RESOLVED"

    # 2. Risk Register evaluation
    critical_risks = risks.get_critical_unmitigated_risks()
    assert len(critical_risks) == 0  # Default seeded risks are MITIGATED
    print("    [PASS] Support operations ticketing & risk register verified")

def test_user_feedback_and_go_no_go_production_gate():
    print(">>> 6. Testing User Feedback & Go/No-Go Production Gate...")
    feedback = UserFeedbackCollector()
    gate = ProductionGoNoGoGate()

    # 1. Feedback metrics
    feedback.submit_feedback("ONBOARDING", 5, "EASE_OF_USE", "Seamless Aadhaar verification")
    feedback.submit_feedback("VERIFICATION", 5, "SPEED", "Instant degree verification")
    feedback.submit_feedback("PROOF", 4, "SECURITY", "Clear QR code proof presentation")

    csat = feedback.calculate_csat_metrics()
    assert csat["averageRating"] >= 4.0
    assert csat["satisfactionPct"] == "100.0%"

    # 2. Go / No-Go Gate Evaluation: All 5 dimensions required
    gate.record_dimension_evaluation("SECURITY", True, "Penetration tests passed, 0 CVEs", "CISO")
    gate.record_dimension_evaluation("PRIVACY", True, "DPDP Act compliance audit passed", "CPO")
    gate.record_dimension_evaluation("RELIABILITY", True, "99.96% availability across pilot", "SRE_LEAD")
    gate.record_dimension_evaluation("UX", True, "100% CSAT satisfaction across pilot users", "HEAD_OF_DESIGN")
    gate.record_dimension_evaluation("OPERATIONS", True, "Support runbooks and 24/7 on-call active", "VP_OPS")

    all_passed, gate_info = gate.evaluate_overall_readiness()
    assert all_passed is True
    assert gate_info["decision"] == "GO"

    # 3. Authorize Staged Traffic Ramp (5% -> 15% -> 30% -> 60% -> 100%)
    ok_ramp, msg_ramp, pct = gate.ramp_traffic(TrafficRampStage.STAGE_1)
    assert ok_ramp is True
    assert pct == 5

    ok_ramp_ga, msg_ramp_ga, pct_ga = gate.ramp_traffic(TrafficRampStage.STAGE_5_GA)
    assert ok_ramp_ga is True
    assert pct_ga == 100

    # 4. Pilot Dashboard Snapshot
    gov = PilotGovernanceManager()
    support = SupportOperationsService()
    risks = PilotRiskRegister()
    dashboard = PilotDashboardService(gov, support, risks, feedback, gate)
    summary = dashboard.get_dashboard_summary()

    assert summary["kpis"]["verificationSuccessRate"] == "92.4%"
    assert summary["launchReadiness"]["decision"] == "GO"
    print("    [PASS] User feedback CSAT, Go/No-Go production gate & staged traffic ramp verified")

def run_all_pilot_tests():
    print("=" * 80)
    print("DIGIIN PHASE 25 CONTROLLED PILOT & PRODUCTION VALIDATION TEST MATRIX")
    print("=" * 80)
    test_pilot_governance_and_boundary_enforcement()
    test_organization_onboarding_checklist()
    test_provider_transaction_reconciliation()
    test_end_to_end_proof_verification_and_revocation()
    test_support_operations_and_risk_register()
    test_user_feedback_and_go_no_go_production_gate()
    print("=" * 80)
    print("SUCCESS: ALL 6 CONTROLLED PILOT & VALIDATION TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_pilot_tests()
