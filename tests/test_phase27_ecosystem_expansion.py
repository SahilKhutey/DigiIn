"""
DigiIn Automated Trust Network Expansion & Ecosystem Operations Test Suite (Phase 27)
Validates Federation Management, Institutional Readiness, Accreditation Lifecycles, Multi-Factor Trust Policies, Composite Claims, Selective Disclosure, Governance, and Fraud Anomaly Throttling.
"""

import sys
import os

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.ecosystem import (
    FederationManager,
    OrganizationReadinessScorer,
    AccreditationEngine,
    AssuranceProfile,
    TrustPolicyEngine,
    CompositeClaimEngine,
    ClaimCatalog,
    MultiClaimPresentationManager,
    SelectiveDisclosureEngine,
    NetworkGovernanceEngine,
    NetworkAnalyticsService,
    FraudAbuseIntelligence,
    AbuseRiskState,
)

def test_federation_and_readiness_scoring():
    print(">>> 1. Testing Trust Federation Management & Readiness Scoring...")
    fed_mgr = FederationManager()

    # 1. Check pre-seeded federation
    assert fed_mgr.is_organization_in_federation("fed_higher_education_india", "org_delhi_univ") is True
    assert fed_mgr.is_organization_in_federation("fed_higher_education_india", "org_unregistered_corp") is False

    # 2. Add member to federation
    ok_add, msg_add, mem = fed_mgr.add_member("fed_higher_education_india", "org_iit_bombay", "ISSUER")
    assert ok_add is True
    assert fed_mgr.is_organization_in_federation("fed_higher_education_india", "org_iit_bombay") is True

    # 3. 6-Dimension Readiness Scorer
    complete_dims = {
        "identity": True, "authority": True, "security": True,
        "privacy": True, "integration": True, "operations": True
    }
    is_ready, r_info = OrganizationReadinessScorer.calculate_readiness(complete_dims)
    assert is_ready is True
    assert r_info["completionPct"] == "100.0%"

    # Incomplete dimensions -> Not Ready
    incomplete_dims = {"identity": True, "authority": True, "security": False}
    is_ready_bad, r_info_bad = OrganizationReadinessScorer.calculate_readiness(incomplete_dims)
    assert is_ready_bad is False
    assert "security" in r_info_bad["missingDimensions"]
    print("    [PASS] Federation management and institutional readiness scoring verified")

def test_accreditation_and_trust_policies():
    print(">>> 2. Testing Issuer/Verifier Accreditation & Multi-Factor Trust Policies...")
    acc_engine = AccreditationEngine()
    policy_engine = TrustPolicyEngine(acc_engine)

    # 1. Authoritative accreditation check
    assert acc_engine.is_issuer_accredited_for_claim("org_delhi_univ", "education.degree") is True
    assert acc_engine.is_issuer_accredited_for_claim("org_delhi_univ", "licence.driving") is False

    # 2. Policy Evaluation: All valid -> ALLOW
    dec_allow = policy_engine.evaluate_policy(
        subject_id="DGI-7K4M-X9P2",
        verifier_org_id="org_ministry_education",
        issuer_org_id="org_delhi_univ",
        claim_type="education.degree",
        purpose="SCHOLARSHIP_ELIGIBILITY",
        consent_granted=True,
        claim_status="ACTIVE"
    )
    assert dec_allow.decision == "ALLOW"
    assert dec_allow.reason_code == "AUTHORIZED_POLICY_COMPLIANT"

    # 3. Policy Evaluation: Consent missing -> DENY
    dec_no_consent = policy_engine.evaluate_policy(
        subject_id="DGI-7K4M-X9P2",
        verifier_org_id="org_ministry_education",
        issuer_org_id="org_delhi_univ",
        claim_type="education.degree",
        purpose="SCHOLARSHIP_ELIGIBILITY",
        consent_granted=False,
        claim_status="ACTIVE"
    )
    assert dec_no_consent.decision == "DENY"
    assert "CONSENT" in dec_no_consent.reason_code

    # 4. Policy Evaluation: Claim Revoked -> DENY
    dec_revoked = policy_engine.evaluate_policy(
        subject_id="DGI-7K4M-X9P2",
        verifier_org_id="org_ministry_education",
        issuer_org_id="org_delhi_univ",
        claim_type="education.degree",
        purpose="SCHOLARSHIP_ELIGIBILITY",
        consent_granted=True,
        claim_status="REVOKED"
    )
    assert dec_revoked.decision == "DENY"
    assert "CLAIM_STATUS_INVALID" in dec_revoked.reason_code
    print("    [PASS] Accreditation lifecycles and multi-factor trust policies verified")

def test_derived_and_composite_claims():
    print(">>> 3. Testing Composite & Derived Claims Engine...")
    comp_engine = CompositeClaimEngine()

    # 1. Eligible scholarship claim (Degree Verified + CGPA 8.5)
    claims_pass = {"degree_status": "VERIFIED", "cgpa": 8.5}
    is_ok, dclaim_pass = comp_engine.evaluate_composite_claim(
        subject_id="DGI-7K4M-X9P2",
        derived_type="scholarship.eligibility",
        rule_id="SCHOLARSHIP_ELIGIBILITY_V2",
        source_claim_ids=["clm_degree_01"],
        claim_values=claims_pass
    )
    assert is_ok is True
    assert dclaim_pass.result == "ELIGIBLE"
    assert dclaim_pass.audit_explanation["cgpaSatisfied"] is True

    # 2. Ineligible scholarship claim (CGPA 6.2 < 7.0)
    claims_fail = {"degree_status": "VERIFIED", "cgpa": 6.2}
    is_ok_fail, dclaim_fail = comp_engine.evaluate_composite_claim(
        subject_id="DGI-7K4M-X9P2",
        derived_type="scholarship.eligibility",
        rule_id="SCHOLARSHIP_ELIGIBILITY_V2",
        source_claim_ids=["clm_degree_01"],
        claim_values=claims_fail
    )
    assert is_ok_fail is False
    assert dclaim_fail.result == "INELIGIBLE"
    print("    [PASS] Composite claim evaluation with transparent audit reasoning verified")

def test_selective_disclosure_and_claim_catalog():
    print(">>> 4. Testing Selective Disclosure & Zero-PII Claim Discovery Catalog...")
    # 1. Zero-PII Claim Discovery Catalog
    catalog = ClaimCatalog()
    all_entries = catalog.list_catalog()
    assert len(all_entries) >= 4

    edu_entries = catalog.list_catalog(domain_filter="EDUCATION")
    assert len(edu_entries) >= 1
    assert edu_entries[0]["claimType"] == "education.degree"

    # 2. Selective Disclosure Engine
    full_address = {
        "houseNo": "42-B",
        "street": "Shanti Path",
        "city": "New Delhi",
        "state": "Delhi",
        "pincode": "110001"
    }
    # Verifier only requests "state"
    projected = SelectiveDisclosureEngine.project_selective_fields(full_address, ["state"])
    assert "state" in projected
    assert "street" not in projected
    assert "houseNo" not in projected

    # 3. Multi-Claim Presentation Bundle
    bundle_mgr = MultiClaimPresentationManager()
    bundle = bundle_mgr.create_presentation_bundle(
        subject_id="DGI-7K4M-X9P2",
        target_verifier="org_ministry_education",
        purpose="SCHOLARSHIP_ELIGIBILITY",
        claims_with_requested_fields=[
            {"claim_id": "clm_01", "type": "education.degree", "value": {"degree": "B.Tech", "gpa": 9.2}, "fields": ["degree"], "issuer_id": "iss_du"},
            {"claim_id": "clm_02", "type": "identity.address", "value": full_address, "fields": ["state"], "issuer_id": "iss_uidai"},
        ]
    )
    assert len(bundle.disclosed_claims) == 2
    assert bundle.target_verifier == "org_ministry_education"
    print("    [PASS] Selective disclosure & multi-claim bundle presentations verified")

def test_governance_and_fraud_abuse_intelligence():
    print(">>> 5. Testing Network Governance & Fraud Abuse Anomaly Detection...")
    # 1. Governance Decision Engine
    gov_engine = NetworkGovernanceEngine()
    decision = gov_engine.record_decision(
        subject_type="ORGANIZATION",
        subject_id="org_iit_delhi",
        decision="APPROVE",
        reason="Accreditation audit and pen-testing passed",
        approvers=["TRUST_ADMIN_01", "SECURITY_ADMIN_02"]
    )
    assert decision.decision == "APPROVE"
    assert len(decision.approved_by) == 2

    # 2. Ecosystem Analytics
    metrics = NetworkAnalyticsService.get_ecosystem_metrics()
    assert metrics["adoption"]["activeOrganizations"] == 128
    assert metrics["operations"]["availabilityPct"] == "99.98%"

    # 3. Fraud & Abuse Intelligence
    fraud_guard = FraudAbuseIntelligence(burst_threshold_per_min=5, critical_burst_threshold=10)
    verifier_ip = "verifier_suspicious_bot_01"

    # Send 5 requests -> NORMAL / MONITORED
    for _ in range(5):
        st, ok = fraud_guard.track_request(verifier_ip)
        assert ok is True

    # 6th burst request -> Throttled!
    st6, ok6 = fraud_guard.track_request(verifier_ip)
    assert ok6 is False
    assert st6 == AbuseRiskState.THROTTLED
    print("    [PASS] Network governance and fraud anomaly throttling verified")

def run_all_ecosystem_tests():
    print("=" * 80)
    print("DIGIIN PHASE 27 TRUST NETWORK EXPANSION & ECOSYSTEM TEST MATRIX")
    print("=" * 80)
    test_federation_and_readiness_scoring()
    test_accreditation_and_trust_policies()
    test_derived_and_composite_claims()
    test_selective_disclosure_and_claim_catalog()
    test_governance_and_fraud_abuse_intelligence()
    print("=" * 80)
    print("SUCCESS: ALL 5 TRUST NETWORK EXPANSION & ECOSYSTEM TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_ecosystem_tests()
