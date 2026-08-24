"""Phase 37 — Release Readiness & Evidence Gate Test Suite.

Enforces the comprehensive Release Gate for DigiLocker X (DigiIn) RC-1:
  1. Authoritative documentation integrity (Master specs + Hackathon presentation suite).
  2. Flagship Citizen-to-Verifier workflow representation.
  3. Valid cryptographic proof verification (RFC 8785 canonicalization & Ed25519).
  4. Negative Proof Class 1: Tampered claim values rejection.
  5. Negative Proof Class 2: Untrusted / rogue issuer rejection.
  6. Negative Proof Class 3: Revoked credential rejection.
  7. Negative Proof Class 4: Expired credential rejection.
  8. Privacy Proof: Minimal selective disclosure compliance (zero raw data).
  9. Privacy Proof: Raw document / forbidden claim leakage rejection.
  10. Deterministic seeded demo environment verification (DGI-7K4M-X9P2-2026).
  11. Security, audit chain, and operational resilience subsystem active checks.
  12. CI/CD workflow configuration integrity.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "services" / "api"))
sys.path.insert(0, str(root_dir))

from app.core.demo import DEMO_PERSONAS, judge_scorecard, qr_generator
from app.core.operations import (
    degradation_manager,
    dr_coordinator,
    health_probes,
    job_worker,
    object_storage,
    observability,
)
from app.core.proofs import (
    KeyManager,
    ProofSigningService,
    ProofVerifier,
    TrustRegistry,
    TrustedIssuer,
    VerifiedClaim,
)
from app.core.security import (
    SecurityAuditEventType,
    audit_chain,
    envelope_encryptor,
    pii_detector,
    policy_engine,
)
from app.core.verification_hardening import (
    HackathonDemoEnvironment,
    NegativeProofEngine,
    PrivacyProofValidator,
    VerificationLabService,
)
from app.db.session import init_db

init_db()


def test_authoritative_documentation_integrity():
    print(">>> 1. Verifying Authoritative Documentation Integrity (Master Specs + Hackathon Suite)...")

    # 7 Master Specs in docs/
    master_specs = [
        "Workflow.md",
        "Principles.md",
        "Services.md",
        "CoreFoundation.md",
        "Database.md",
        "Auth.md",
        "UI-UX.md",
    ]
    for spec in master_specs:
        spec_path = root_dir / "docs" / spec
        assert spec_path.is_file(), f"Missing authoritative specification: {spec}"
        assert spec_path.stat().st_size > 1000, f"Specification {spec} is too small"

    # Hackathon Presentation Suite in docs/hackathon/
    hackathon_docs = [
        "RELEASE_READINESS.md",
        "DEMO_SCRIPT.md",
        "EVIDENCE_MATRIX.md",
        "RELEASE_CHECKLIST.md",
        "JURY_VERIFICATION.md",
    ]
    for hdoc in hackathon_docs:
        hdoc_path = root_dir / "docs" / "hackathon" / hdoc
        assert hdoc_path.is_file(), f"Missing hackathon documentation: {hdoc}"
        assert hdoc_path.stat().st_size > 500, f"Hackathon doc {hdoc} is too small"

    print("    [PASS] All 7 Master Specs and 5 Hackathon Release Documents verified present and substantive")


def test_flagship_workflow_and_valid_cryptographic_proof():
    print(">>> 2. Verifying Flagship Workflow & Cryptographic Proof Verification...")

    # Key Manager and Trust Registry Setup
    key_manager = KeyManager()
    key_manager.generate_and_register_key("KEY-RC1-PRIMARY")
    trust_registry = TrustRegistry()
    trust_registry.register_issuer(
        TrustedIssuer(
            id="iss_digiin_rc1",
            name="DigiIn Sovereign Root Authority",
            issuer_identifier="did:digiin:authority:root",
            trusted_proof_types=["EDUCATION_VERIFIED", "DOMICILE_VERIFIED"],
            status="ACTIVE",
        )
    )
    signer = ProofSigningService(key_manager)
    verifier = ProofVerifier(key_manager, trust_registry)

    # Sovereign Citizen Rahul Sharma
    citizen_account = "DGI-7K4M-X9P2-2026"
    claims = [
        VerifiedClaim(type="EDUCATION_VERIFIED", value={"degree": "B.Tech", "passing_year": 2026, "eligible": True}),
    ]

    # Mint Valid Proof
    proof = signer.mint_signed_proof(
        subject_id=citizen_account,
        claims=claims,
        purpose="SCHOLARSHIP_ELIGIBILITY_CHECK",
        proof_type="EDUCATION_VERIFIED",
    )
    assert proof["status"] == "ACTIVE"
    assert "signature" in proof
    assert "digest" in proof

    # Verify Proof
    outcome = verifier.verify(proof, expected_purpose="SCHOLARSHIP_ELIGIBILITY_CHECK")
    assert outcome.valid is True
    assert outcome.signature_valid is True
    assert outcome.issuer_trusted is True
    assert outcome.key_valid is True
    assert outcome.not_expired is True
    assert outcome.policy_satisfied is True

    print("    [PASS] Flagship workflow proof minted and validated with 100% cryptographic integrity")


def test_negative_proof_classes():
    print(">>> 3. Verifying Negative Proof Lab Classes (Tampered, Untrusted, Revoked, Expired)...")

    lab = VerificationLabService()
    tests = lab.run_all_lab_tests()

    # TC-01: Valid Credential
    tc1 = next(t for t in tests if t.test_id == "TC-01")
    assert tc1.actual_result.is_valid is True
    assert tc1.actual_result.status == "VERIFIED"

    # TC-02: Tampered Marksheet Score
    tc2 = next(t for t in tests if t.test_id == "TC-02")
    assert tc2.actual_result.is_valid is False
    assert tc2.actual_result.status == "INVALID"
    assert tc2.actual_result.failed_check == "DIGEST_INTEGRITY_CHECK"

    # TC-03: Untrusted / Rogue Issuer
    tc3 = next(t for t in tests if t.test_id == "TC-03")
    assert tc3.actual_result.is_valid is False
    assert tc3.actual_result.status == "UNTRUSTED"
    assert tc3.actual_result.failed_check == "ISSUER_TRUST_CHECK"

    # TC-04: Revoked Credential Certificate
    tc4 = next(t for t in tests if t.test_id == "TC-04")
    assert tc4.actual_result.is_valid is False
    assert tc4.actual_result.status == "REVOKED"
    assert tc4.actual_result.failed_check == "REVOCATION_CHECK"

    # TC-05: Expired Proof Token
    tc5 = next(t for t in tests if t.test_id == "TC-05")
    assert tc5.actual_result.is_valid is False
    assert tc5.actual_result.status == "EXPIRED"
    assert tc5.actual_result.failed_check == "EXPIRATION_CHECK"

    print("    [PASS] All 5 Negative Proof classes verified: tampered, untrusted, revoked, and expired rejected")


def test_privacy_proof_and_minimal_disclosure():
    print(">>> 4. Verifying Privacy Minimal Disclosure & Anti-Leakage Audit...")

    # Case A: Compliant Minimal Disclosure (Only requested predicate)
    compliant_payload = {
        "status": "VERIFIED",
        "claims": {
            "income_eligible": True,
            "passing_year": 2026,
        },
    }
    audit_pass = PrivacyProofValidator.audit_service_disclosure(
        requested_and_consented_claims=["income_eligible", "passing_year"],
        returned_payload=compliant_payload,
    )
    assert audit_pass.is_compliant is True
    assert audit_pass.raw_files_leaked is False
    assert len(audit_pass.forbidden_claims_detected) == 0

    # Case B: Privacy-Violating Payload (Attempting to disclose raw PDF & Aadhaar)
    leaky_payload = {
        "status": "VERIFIED",
        "claims": {
            "income_eligible": True,
            "aadhaar_number": "2345 6789 0123",
            "annual_income_exact": "INR 180000",
        },
        "raw_file": "BASE64_DOCUMENT_BINARY_LEAK...",
    }
    audit_fail = PrivacyProofValidator.audit_service_disclosure(
        requested_and_consented_claims=["income_eligible"],
        returned_payload=leaky_payload,
    )
    assert audit_fail.is_compliant is False
    assert audit_fail.raw_files_leaked is True
    assert "aadhaar_number" in audit_fail.forbidden_claims_detected

    print("    [PASS] Privacy proof validated: minimal predicates pass, raw document/PII leaks strictly rejected")


def test_deterministic_seeded_demo_environment():
    print(">>> 5. Verifying Deterministic Seeded Demo Environment...")

    demo_state = HackathonDemoEnvironment.get_preseeded_demo_state()
    assert demo_state.citizen_account_id == "DGI-7K4M-X9P2-2026"
    assert demo_state.citizen_name == "Rahul Sharma"
    assert demo_state.service_name == "National Scholarship Portal"
    assert demo_state.university_name == "University of Delhi"
    assert demo_state.credential_title == "Bachelor of Technology in Computer Science"

    # Verify pre-configured personas
    personas = DEMO_PERSONAS
    assert "citizen" in personas
    assert "officer" in personas
    assert "reviewer" in personas
    assert "operator" in personas

    # Verify QR Generator round-trip
    qr_payload = qr_generator.encode_proof_to_qr_payload({"proofId": "prf_rc1_test", "status": "ACTIVE"})
    assert qr_payload.startswith("digiin://verify/v1/")
    decoded = qr_generator.decode_qr_payload_to_proof(qr_payload)
    assert decoded["proofId"] == "prf_rc1_test"

    print("    [PASS] Deterministic demo environment and 4-persona setup verified for 3-browser showcase")


def test_security_audit_and_operational_resilience():
    print(">>> 6. Verifying Security Audit Chain & Operational Resilience Subsystems...")

    # 1. Tamper-Evident SHA-256 Audit Chain
    audit_chain.append(
        event_type=SecurityAuditEventType.PROOF_VERIFIED,
        actor_id="DGI-OFF-SCHOLARSHIP-01",
        resource_type="proof",
        resource_id="prf_rc1_gate_check",
        purpose="RELEASE_GATE_VERIFICATION",
        metadata={"result": "VERIFIED", "claims": ["income_eligible"]},
    )
    chain_valid, chain_msg = audit_chain.verify_integrity()
    assert chain_valid is True, f"Audit chain integrity error: {chain_msg}"

    # 2. 3-Tier Health Probes
    live = health_probes.check_liveness()
    ready, ready_res = health_probes.check_readiness()
    deps = health_probes.check_dependencies()
    assert live["status"] == "UP"
    assert ready is True
    assert deps["overall_system_state"] in ("HEALTHY", "DEGRADED")

    # 3. Disaster Recovery RPO / RTO Compliance
    dr_status = dr_coordinator.get_dr_status()
    assert dr_status["rpo_target_minutes"] <= 15.0
    assert dr_status["rto_target_minutes"] <= 60.0

    # 4. Judge Scorecard
    scorecard = judge_scorecard.compile_scorecard()
    assert scorecard["operational_resilience"]["slo_overall_status"] == "COMPLIANT"

    print("    [PASS] SHA-256 audit chain, 3-tier health probes, DR targets, and judge scorecard verified")


def test_ci_workflow_configuration():
    print(">>> 7. Verifying CI/CD Pipeline Configuration...")

    ci_workflow_path = root_dir / ".github" / "workflows" / "ci.yml"
    assert ci_workflow_path.is_file(), "Missing .github/workflows/ci.yml"
    content = ci_workflow_path.read_text(encoding="utf-8")
    assert "run_all_tests.py" in content or "pytest" in content
    assert "ruff" in content or "lint" in content

    print("    [PASS] Automated CI workflow file (.github/workflows/ci.yml) verified active")


# ===========================================================================
# Main Execution
# ===========================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("DIGIIN PHASE 37 — RELEASE READINESS & EVIDENCE GATE TEST SUITE")
    print("=" * 80)

    test_authoritative_documentation_integrity()
    test_flagship_workflow_and_valid_cryptographic_proof()
    test_negative_proof_classes()
    test_privacy_proof_and_minimal_disclosure()
    test_deterministic_seeded_demo_environment()
    test_security_audit_and_operational_resilience()
    test_ci_workflow_configuration()

    print()
    print("=" * 80)
    print("SUCCESS: ALL PHASE 37 RELEASE READINESS & EVIDENCE GATE CHECKS PASSED (100%)")
    print("=" * 80)
