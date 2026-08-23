"""
DigiIn Automated Trust Network & Interoperability Test Suite (Phase 26)
Validates Issuer/Verifier Registries, Scoped Trust Relationships, Claim Schemas, Claim Issuance, Audience-Restricted Presentation, Revocation, Anti-Enumeration, and Interoperability Protocol Adapters.
"""

import sys
import os

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.trust_network import (
    IssuerRegistry,
    VerifierRegistry,
    TrustRelationshipEngine,
    ClaimSchemaRegistry,
    ClaimIssuanceEngine,
    ClaimPresentationEngine,
    TrustProtocolAdapter,
    AntiEnumerationGuard,
    TrustNetworkMonitor,
    ClaimStatus,
)

def test_issuer_and_verifier_registries():
    print(">>> 1. Testing Issuer & Verifier Registries...")
    iss_reg = IssuerRegistry()
    ver_reg = VerifierRegistry()

    # 1. Authoritative Issuer check
    assert iss_reg.is_issuer_authorized_for_claim("iss_delhi_university", "education.degree") is True
    assert iss_reg.is_issuer_authorized_for_claim("iss_delhi_university", "licence.driving") is False

    # 2. Verifier Access & Purpose check
    ok_ver, _ = ver_reg.validate_verifier_access(
        verifier_id="ver_scholarship_portal",
        claim_type="education.degree",
        purpose="SCHOLARSHIP_ELIGIBILITY"
    )
    assert ok_ver is True

    # 3. Unauthorized Purpose -> REJECT
    ok_unauth_purp, err_purp = ver_reg.validate_verifier_access(
        verifier_id="ver_scholarship_portal",
        claim_type="education.degree",
        purpose="UNAUTHORIZED_MARKETING"
    )
    assert ok_unauth_purp is False
    assert "PURPOSE_NOT_PERMITTED" in err_purp
    print("    [PASS] Issuer & Verifier Registries and Scoped Purpose Rules verified")

def test_scoped_trust_relationships():
    print(">>> 2. Testing Scoped Cross-Organization Trust Relationships...")
    rel_engine = TrustRelationshipEngine()

    # 1. Pre-seeded scoped relationship: Delhi Univ -> Ministry of Education for education.degree
    ok_rel, _ = rel_engine.validate_relationship(
        issuer_org="org_delhi_univ",
        verifier_org="org_ministry_education",
        claim_type="education.degree",
        purpose="SCHOLARSHIP_ELIGIBILITY"
    )
    assert ok_rel is True

    # 2. Unscoped Claim Type -> REJECT
    ok_bad_claim, err_claim = rel_engine.validate_relationship(
        issuer_org="org_delhi_univ",
        verifier_org="org_ministry_education",
        claim_type="licence.driving",
        purpose="SCHOLARSHIP_ELIGIBILITY"
    )
    assert ok_bad_claim is False
    assert "CLAIM_TYPE_NOT_SCOPED" in err_claim
    print("    [PASS] Scoped trust relationships verified")

def test_claim_schema_and_issuance():
    print(">>> 3. Testing Immutable Claim Schema Registry & Issuance Engine...")
    iss_reg = IssuerRegistry()
    schema_reg = ClaimSchemaRegistry()
    issuance_engine = ClaimIssuanceEngine(iss_reg, schema_reg)

    valid_degree = {
        "degree": "Bachelor of Technology in Computer Science",
        "institution": "University of Delhi",
        "year": 2025,
        "cgpa": 9.4
    }

    # 1. Issue claim with valid schema -> SUCCESS
    ok_issue, err_issue, claim = issuance_engine.issue_claim(
        issuer_id="iss_delhi_university",
        subject_id="DGI-7K4M-X9P2",
        claim_type="education.degree",
        payload=valid_degree
    )
    assert ok_issue is True
    assert claim.id.startswith("clm_")
    assert claim.status == ClaimStatus.ACTIVE

    # 2. Issue claim with missing required field -> REJECT
    invalid_degree = {"degree": "B.Tech"}  # Missing institution and year
    ok_bad, err_bad, _ = issuance_engine.issue_claim(
        issuer_id="iss_delhi_university",
        subject_id="DGI-7K4M-X9P2",
        claim_type="education.degree",
        payload=invalid_degree
    )
    assert ok_bad is False
    assert "SCHEMA_VALIDATION_FAILED" in err_bad
    print("    [PASS] Schema validation and claim issuance verified")

def test_audience_restricted_presentation_and_anti_replay():
    print(">>> 4. Testing Audience-Restricted Presentation & Anti-Replay Nonce...")
    iss_reg = IssuerRegistry()
    ver_reg = VerifierRegistry()
    schema_reg = ClaimSchemaRegistry()
    issuance_engine = ClaimIssuanceEngine(iss_reg, schema_reg)
    pres_engine = ClaimPresentationEngine(ver_reg, issuance_engine)

    # Issue claim
    _, _, claim = issuance_engine.issue_claim(
        issuer_id="iss_delhi_university",
        subject_id="DGI-7K4M-X9P2",
        claim_type="education.degree",
        payload={"degree": "B.Tech", "institution": "University of Delhi", "year": 2025}
    )

    # 1. Create audience-restricted presentation with unique nonce
    nonce = "nonce_random_991823"
    ok_pres, _, pres = pres_engine.create_presentation(
        subject_id="DGI-7K4M-X9P2",
        verifier_id="ver_scholarship_portal",
        purpose="SCHOLARSHIP_ELIGIBILITY",
        claim_ids=[claim.id],
        nonce=nonce
    )
    assert ok_pres is True
    assert pres.target_audience == "ver_scholarship_portal"

    # 2. Verify by authorized audience with matching nonce -> SUCCESS
    ok_v, msg_v = pres_engine.verify_presentation(
        presentation=pres,
        expected_verifier_id="ver_scholarship_portal",
        expected_purpose="SCHOLARSHIP_ELIGIBILITY",
        expected_nonce=nonce
    )
    assert ok_v is True

    # 3. Audience Mismatch -> REJECT (presentation cannot be sent to an unrelated employer)
    ok_bad_aud, err_aud = pres_engine.verify_presentation(
        presentation=pres,
        expected_verifier_id="ver_unrelated_employer",
        expected_purpose="SCHOLARSHIP_ELIGIBILITY",
        expected_nonce=nonce
    )
    assert ok_bad_aud is False
    assert "AUDIENCE_MISMATCH" in err_aud

    # 4. Replay attempt with mismatched nonce -> REJECT
    ok_bad_nonce, err_nonce = pres_engine.verify_presentation(
        presentation=pres,
        expected_verifier_id="ver_scholarship_portal",
        expected_purpose="SCHOLARSHIP_ELIGIBILITY",
        expected_nonce="nonce_different_replay_attack"
    )
    assert ok_bad_nonce is False
    assert "NONCE_MISMATCH" in err_nonce
    print("    [PASS] Audience restriction and anti-replay nonce verified")

def test_claim_revocation_and_authoritative_status():
    print(">>> 5. Testing Instant Claim Revocation & Status Lookup...")
    iss_reg = IssuerRegistry()
    ver_reg = VerifierRegistry()
    schema_reg = ClaimSchemaRegistry()
    issuance_engine = ClaimIssuanceEngine(iss_reg, schema_reg)
    pres_engine = ClaimPresentationEngine(ver_reg, issuance_engine)

    _, _, claim = issuance_engine.issue_claim(
        issuer_id="iss_delhi_university",
        subject_id="DGI-7K4M-X9P2",
        claim_type="education.degree",
        payload={"degree": "B.Tech", "institution": "University of Delhi", "year": 2025}
    )

    # Initial status is ACTIVE
    assert issuance_engine.check_claim_status(claim.id) == ClaimStatus.ACTIVE

    # Revoke claim at authoritative source
    assert issuance_engine.revoke_claim(claim.id, reason="FRAUDULENT_RECORD") is True
    assert issuance_engine.check_claim_status(claim.id) == ClaimStatus.REVOKED

    # Attempt to present revoked claim -> REJECT
    ok_p, err_p, _ = pres_engine.create_presentation(
        subject_id="DGI-7K4M-X9P2",
        verifier_id="ver_scholarship_portal",
        purpose="SCHOLARSHIP_ELIGIBILITY",
        claim_ids=[claim.id]
    )
    assert ok_p is False
    assert "CLAIM_INACTIVE" in err_p
    print("    [PASS] Authoritative status & instant revocation propagation verified")

def test_anti_enumeration_and_interop_adapter():
    print(">>> 6. Testing Anti-Enumeration Guard & Interoperability Adapter...")
    # 1. Anti-Enumeration Guard
    guard = AntiEnumerationGuard(max_probes_per_window=3, window_seconds=60.0)
    ip = "198.51.100.42"
    ok1, _ = guard.record_and_check_probe(ip, "DGI-USER-001")
    ok2, _ = guard.record_and_check_probe(ip, "DGI-USER-002")
    ok3, _ = guard.record_and_check_probe(ip, "DGI-USER-003")
    ok4, msg4 = guard.record_and_check_probe(ip, "DGI-USER-004")

    assert ok1 and ok2 and ok3 is True
    assert ok4 is False  # 4th probe triggers enumeration throttle
    assert "RATE_LIMIT_ENUMERATION_ATTACK_DETECTED" in msg4

    # 2. Interoperability Protocol Adapter
    iss_reg = IssuerRegistry()
    ver_reg = VerifierRegistry()
    schema_reg = ClaimSchemaRegistry()
    issuance_engine = ClaimIssuanceEngine(iss_reg, schema_reg)
    pres_engine = ClaimPresentationEngine(ver_reg, issuance_engine)

    adapter = TrustProtocolAdapter(iss_reg, ver_reg, schema_reg, issuance_engine, pres_engine)

    # Issue
    ok_i, _, clm = adapter.issue_claim(
        issuer_id="iss_delhi_university",
        subject_id="DGI-SBX-001",
        claim_type="education.degree",
        payload={"degree": "M.Sc", "institution": "University of Delhi", "year": 2024}
    )
    assert ok_i is True

    # Status
    status_res = adapter.check_status(clm.id)
    assert status_res["status"] == "ACTIVE"

    # Present & Verify
    ok_pr, _, pres = adapter.present_claim("DGI-SBX-001", "ver_scholarship_portal", "SCHOLARSHIP_ELIGIBILITY", [clm.id])
    assert ok_pr is True

    ok_vr, msg_vr = adapter.verify_claim(pres, "ver_scholarship_portal", "SCHOLARSHIP_ELIGIBILITY")
    assert ok_vr is True
    print("    [PASS] Anti-enumeration defense & interoperability protocol adapter verified")

def run_all_trust_network_tests():
    print("=" * 80)
    print("DIGIIN PHASE 26 TRUST NETWORK & INTEROPERABILITY TEST MATRIX")
    print("=" * 80)
    test_issuer_and_verifier_registries()
    test_scoped_trust_relationships()
    test_claim_schema_and_issuance()
    test_audience_restricted_presentation_and_anti_replay()
    test_claim_revocation_and_authoritative_status()
    test_anti_enumeration_and_interop_adapter()
    print("=" * 80)
    print("SUCCESS: ALL 6 TRUST NETWORK & INTEROPERABILITY TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_trust_network_tests()
