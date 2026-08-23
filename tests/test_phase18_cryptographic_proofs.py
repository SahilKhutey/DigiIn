"""
DigiIn Automated Cryptographic Proof & Tamper Defense Test Suite (Phase 18)
Validates RFC 8785 canonicalization, Ed25519 digital signatures, multi-stage verification, key rotation, and instant revocation.
"""

import sys
import os
import time

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.proofs import (
    VerifiedClaim,
    ClaimMinimizer,
    KeyManager,
    KeyStatus,
    TrustRegistry,
    TrustedIssuer,
    ProofSigningService,
    ProofVerifier,
    ProofShareService,
)

def test_signature_validity_and_tamper_detection():
    print(">>> 1. Testing Cryptographic Signature & Tamper Detection...")
    key_manager = KeyManager()
    key_manager.generate_and_register_key("KEY-2026-PRIMARY")
    trust_registry = TrustRegistry()
    
    signer = ProofSigningService(key_manager)
    verifier = ProofVerifier(key_manager, trust_registry)

    claims = [
        VerifiedClaim(type="EDUCATION", value={"degree": "B.Tech", "grade": "Distinction"}),
        VerifiedClaim(type="AGE_ELIGIBILITY", value={"is_18_plus": True}),
    ]

    # Mint valid proof
    proof = signer.mint_signed_proof(
        subject_id="subj_rahul_99",
        claims=claims,
        purpose="COLLEGE_ADMISSION",
        proof_type="EDUCATION_VERIFIED"
    )

    assert proof["status"] == "ACTIVE"
    assert "signature" in proof
    assert "digest" in proof

    # Verify original proof -> PASS
    outcome = verifier.verify(proof, expected_purpose="COLLEGE_ADMISSION")
    assert outcome.valid is True
    assert outcome.signature_valid is True
    assert outcome.issuer_trusted is True

    # Tamper with claim payload (Attacker elevates grade to 100%)
    tampered_proof = dict(proof)
    tampered_proof["claims"] = [
        {"type": "EDUCATION", "value": {"degree": "B.Tech", "grade": "TOPPER_100_PERCENT"}}
    ]
    tampered_outcome = verifier.verify(tampered_proof)
    assert tampered_outcome.valid is False
    assert tampered_outcome.signature_valid is False
    assert "SIGNATURE_INVALID" in tampered_outcome.reason

    # Tamper with subject ID
    tampered_subject_proof = dict(proof)
    tampered_subject_proof["subject"] = "subj_attacker_impersonator"
    tampered_sub_outcome = verifier.verify(tampered_subject_proof)
    assert tampered_sub_outcome.valid is False
    assert tampered_sub_outcome.signature_valid is False
    print("    [PASS] Cryptographic signing & tamper rejection verified")

def test_multi_stage_verification_failures():
    print(">>> 2. Testing Multi-Stage Verification Pipeline Failures...")
    key_manager = KeyManager()
    key_manager.generate_and_register_key("KEY-2026-PRIMARY")
    trust_registry = TrustRegistry()
    
    signer = ProofSigningService(key_manager)
    verifier = ProofVerifier(key_manager, trust_registry)

    claims = [VerifiedClaim(type="EDUCATION", value="PASSED")]
    proof = signer.mint_signed_proof(
        subject_id="subj_42",
        claims=claims,
        purpose="ADMISSION_VERIFICATION"
    )

    # 1. Untrusted Issuer Failure
    untrusted_proof = dict(proof)
    untrusted_proof["issuer"] = "did:untrusted:malicious_entity"
    # Even if attacker signs with their own key, issuer check must fail
    res = verifier.verify(untrusted_proof)
    assert res.valid is False
    assert "ISSUER_UNTRUSTED" in res.reason

    # 2. Status Revoked Failure
    revoked_proof = dict(proof)
    revoked_proof["status"] = "REVOKED"
    res = verifier.verify(revoked_proof)
    assert res.valid is False
    assert res.signature_valid is True  # Signature was mathematically valid
    assert res.status_valid is False    # But rejected due to revocation status
    assert "PROOF_REVOKED" in res.reason

    # 3. Expiration Failure
    res = verifier.verify(proof, now=proof["expiresAt"] + 100)
    assert res.valid is False
    assert res.not_expired is False
    assert "PROOF_EXPIRED" in res.reason

    # 4. Purpose Mismatch / Anti-Replay Failure
    res = verifier.verify(proof, expected_purpose="EMPLOYMENT_BACKGROUND_CHECK")
    assert res.valid is False
    assert res.policy_satisfied is False
    assert "PURPOSE_MISMATCH" in res.reason
    print("    [PASS] Multi-stage verifier rejection branches verified")

def test_key_rotation_and_legacy_proofs():
    print(">>> 3. Testing Key Rotation & Legacy Proof Verification...")
    key_manager = KeyManager()
    key_manager.generate_and_register_key("KEY-2026-GEN1")
    trust_registry = TrustRegistry()
    
    signer = ProofSigningService(key_manager)
    verifier = ProofVerifier(key_manager, trust_registry)

    # Mint proof with Gen 1 key
    proof_gen1 = signer.mint_signed_proof(
        subject_id="subj_legacy_101",
        claims=[VerifiedClaim(type="EDUCATION", value="DEGREE_AWARDED")]
    )
    assert proof_gen1["keyId"] == "KEY-2026-GEN1"

    # Rotate to Gen 2 key
    key_manager.rotate_key("KEY-2026-GEN2")
    assert key_manager.get_active_signing_key().key_id == "KEY-2026-GEN2"
    assert key_manager.get_key("KEY-2026-GEN1").status == KeyStatus.RETIRED

    # Mint new proof with Gen 2 key
    proof_gen2 = signer.mint_signed_proof(
        subject_id="subj_modern_202",
        claims=[VerifiedClaim(type="EDUCATION", value="DEGREE_AWARDED")]
    )
    assert proof_gen2["keyId"] == "KEY-2026-GEN2"

    # Verify BOTH proofs: Legacy Gen 1 proof AND new Gen 2 proof must verify successfully
    res1 = verifier.verify(proof_gen1)
    assert res1.valid is True, f"Legacy proof failed verification after key rotation: {res1.reason}"

    res2 = verifier.verify(proof_gen2)
    assert res2.valid is True, f"Modern proof failed verification: {res2.reason}"

    # If Gen 1 key is REVOKED (e.g. key compromise), legacy proof must be rejected
    key_manager.revoke_key("KEY-2026-GEN1")
    res_compromised = verifier.verify(proof_gen1)
    assert res_compromised.valid is False
    assert "KEY_INVALID" in res_compromised.reason
    print("    [PASS] Key rotation & legacy backward compatibility verified")

def test_privacy_preserving_proof_sharing():
    print(">>> 4. Testing Privacy-Preserving Proof Sharing & QR Resolver...")
    share_service = ProofShareService()
    citizen_id = "citizen_rahul_99"
    proof_id = "prf_01K892M01"

    # Citizen shares only EDUCATION claim
    share = share_service.create_proof_share(
        proof_id=proof_id,
        citizen_id=citizen_id,
        disclosed_claims=["EDUCATION"],
        purpose="UNIVERSITY_VERIFICATION",
        ttl_seconds=600
    )
    assert share["id"].startswith("shr_")
    assert "qr_verification_url" in share

    # Verifier resolves share
    resolved = share_service.resolve_proof_share(share["id"])
    assert resolved is not None
    assert resolved["disclosed_claims"] == ["EDUCATION"]
    assert "ADDRESS" not in resolved["disclosed_claims"]

    # Citizen revokes share session
    revoked = share_service.revoke_proof_share(share["id"], citizen_id=citizen_id)
    assert revoked is True
    assert share_service.resolve_proof_share(share["id"]) is None
    print("    [PASS] Privacy-preserving proof sharing & QR resolver verified")

def run_all_proof_tests():
    print("=" * 80)
    print("DIGIIN PHASE 18 CRYPTOGRAPHIC PROOF & VERIFIABLE CREDENTIALS TEST MATRIX")
    print("=" * 80)
    test_signature_validity_and_tamper_detection()
    test_multi_stage_verification_failures()
    test_key_rotation_and_legacy_proofs()
    test_privacy_preserving_proof_sharing()
    print("=" * 80)
    print("SUCCESS: ALL 4 CRYPTOGRAPHIC PROOF & TAMPER TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_proof_tests()
