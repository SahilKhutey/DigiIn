"""
DigiIn Automated Product Verification Test Suite (Phase 32)
Validates Generic Product Model, Cryptographic Signing, Multi-Point Verification Engine (7 Checks), Lifecycle Statuses, QR Parsing, and Flagship Vertical Slice.
"""

import sys
import os
import time

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.product_verification import (
    DigiInProduct,
    ProductType,
    ProductStatus,
    ProductLifecycleManager,
    ProductVerificationEngine,
    ProductVerificationRequest,
    VerificationOutcomeStatus,
    QRVerifierHelper,
    PublicResponseSanitizer,
)

class MockTrustRegistry:
    def is_trusted(self, issuer_id: str) -> bool:
        return issuer_id in ("iss_delhi_university", "iss_cbse_board", "iss_parivahan")

def test_product_creation_and_opaque_id():
    print(">>> 1. Testing Product Creation & Opaque Product ID...")
    pid = DigiInProduct.generate_product_id()
    assert DigiInProduct.is_valid_product_id(pid) is True
    assert pid.startswith("DGP-")
    assert len(pid.split("-")) == 4

    lifecycle_mgr = ProductLifecycleManager()
    rec = lifecycle_mgr.create_product(
        product_type=ProductType.DIGITAL_CERTIFICATE,
        issuer_id="iss_delhi_university",
        subject_id="subj_rahul_99",
        schema_version="1.0.0",
        claims={"degree": "B.Tech Computer Science", "year": 2025}
    )
    assert rec.product.status == ProductStatus.ACTIVE
    assert rec.signature.algorithm == "Ed25519"
    assert rec.signature.digest_sha256 is not None
    print("    [PASS] Product creation, high-entropy ID & Ed25519 signing verified")

def test_multi_check_verification_valid_and_tampered():
    print(">>> 2. Testing Multi-Check Verification Engine (Valid vs Tampered)...")
    lifecycle_mgr = ProductLifecycleManager()
    trust_reg = MockTrustRegistry()
    engine = ProductVerificationEngine(lifecycle_mgr, trust_reg)

    # 1. Create Valid Product
    rec = lifecycle_mgr.create_product(
        product_type=ProductType.VERIFIABLE_CREDENTIAL,
        issuer_id="iss_delhi_university",
        subject_id="subj_rahul_99",
        schema_version="1.0.0",
        claims={"degree": "B.Tech CS", "grade": "Distinction"}
    )

    # 2. Verify Valid Product -> VERIFIED
    req1 = ProductVerificationRequest(product_id=rec.product.product_id)
    res1 = engine.verify_product(req1)
    assert res1.status == VerificationOutcomeStatus.VERIFIED
    assert res1.assurance_level == "A3_HIGH_ASSURANCE"

    # 3. Tamper with Product Claims -> INVALID
    rec.product.claims["grade"] = "First Class (Tampered)"
    req2 = ProductVerificationRequest(product_id=rec.product.product_id)
    res2 = engine.verify_product(req2)
    assert res2.status == VerificationOutcomeStatus.INVALID
    assert "SIGNATURE" in res2.reason or "signature" in res2.reason.lower()
    print("    [PASS] Multi-check verification & tamper detection verified")

def test_product_lifecycle_status_transitions():
    print(">>> 3. Testing Product Lifecycle Status Transitions (Suspended, Reactivated, Expired, Revoked)...")
    lifecycle_mgr = ProductLifecycleManager()
    trust_reg = MockTrustRegistry()
    engine = ProductVerificationEngine(lifecycle_mgr, trust_reg)

    rec = lifecycle_mgr.create_product(
        product_type=ProductType.DIGITAL_CERTIFICATE,
        issuer_id="iss_delhi_university",
        subject_id="subj_rahul_99",
        schema_version="1.0.0",
        claims={"degree": "B.Tech CS"}
    )
    pid = rec.product.product_id

    # 1. Suspend Product -> SUSPENDED
    assert lifecycle_mgr.suspend_product(pid, reason="FRAUD_INVESTIGATION") is True
    res_susp = engine.verify_product(ProductVerificationRequest(product_id=pid))
    assert res_susp.status == VerificationOutcomeStatus.SUSPENDED

    # 2. Reactivate Product -> VERIFIED
    assert lifecycle_mgr.reactivate_product(pid) is True
    res_react = engine.verify_product(ProductVerificationRequest(product_id=pid))
    assert res_react.status == VerificationOutcomeStatus.VERIFIED

    # 3. Simulate Expiration -> EXPIRED
    rec.product.expires_at = time.time() - 10  # Expired in past
    res_exp = engine.verify_product(ProductVerificationRequest(product_id=pid))
    assert res_exp.status == VerificationOutcomeStatus.EXPIRED
    rec.product.expires_at = time.time() + 86400  # Restore expiry

    # 4. Revoke Product -> REVOKED
    assert lifecycle_mgr.revoke_product(pid, reason="STUDENT_DISQUALIFIED") is True
    res_rev = engine.verify_product(ProductVerificationRequest(product_id=pid))
    assert res_rev.status == VerificationOutcomeStatus.REVOKED
    print("    [PASS] Product lifecycle status transitions (Suspended/Reactivated/Expired/Revoked) verified")

def test_qr_reference_and_public_sanitization():
    print(">>> 4. Testing QR Reference Parsing & Public Response Sanitization...")
    lifecycle_mgr = ProductLifecycleManager()
    trust_reg = MockTrustRegistry()
    engine = ProductVerificationEngine(lifecycle_mgr, trust_reg)

    rec = lifecycle_mgr.create_product(
        product_type=ProductType.VERIFICATION_BADGE,
        issuer_id="iss_cbse_board",
        subject_id="subj_student_01",
        schema_version="1.0.0",
        claims={"badge": "Top 1% National Merit"}
    )
    pid = rec.product.product_id

    # 1. QR Payload Generation & Parsing
    qr_str = QRVerifierHelper.generate_qr_payload(pid)
    assert qr_str == f"digiin://verify/{pid}"
    parsed_id = QRVerifierHelper.parse_qr_payload(qr_str)
    assert parsed_id == pid

    # 2. Verify via QR Payload -> VERIFIED
    qr_req = ProductVerificationRequest(qr_payload=qr_str)
    qr_res = engine.verify_product(qr_req)
    assert qr_res.status == VerificationOutcomeStatus.VERIFIED

    # 3. Public Response Sanitization (Shield internal DB structures)
    public_dict = PublicResponseSanitizer.sanitize_for_public(qr_res)
    assert "verificationId" in public_dict
    assert public_dict["status"] == "VERIFIED"
    assert "claims" not in public_dict  # Protected from public data harvesting
    print("    [PASS] QR reference parsing and public data sanitization verified")

def test_flagship_vertical_slice_e2e():
    print(">>> 5. Testing Flagship Product Verification Vertical Slice...")
    lifecycle_mgr = ProductLifecycleManager()
    trust_reg = MockTrustRegistry()
    engine = ProductVerificationEngine(lifecycle_mgr, trust_reg)

    # 1. University creates and signs Degree Certificate
    rec = lifecycle_mgr.create_product(
        product_type=ProductType.DIGITAL_CERTIFICATE,
        issuer_id="iss_delhi_university",
        subject_id="DGI-7K4M-X9P2",
        schema_version="education.degree.v1",
        claims={"degree": "B.Tech Computer Science", "institution": "University of Delhi", "year": 2026}
    )
    pid = rec.product.product_id

    # 2. Public Verifier verifies product via API -> VERIFIED
    res1 = engine.verify_product(ProductVerificationRequest(product_id=pid, purpose="EMPLOYMENT_CHECK"))
    assert res1.status == VerificationOutcomeStatus.VERIFIED
    assert res1.issuer["trusted"] is True

    # 3. University authoritatively revokes product
    assert lifecycle_mgr.revoke_product(pid, reason="ACADEMIC_MISCONDUCT") is True

    # 4. Verifier re-queries -> REVOKED
    res2 = engine.verify_product(ProductVerificationRequest(product_id=pid, purpose="EMPLOYMENT_CHECK"))
    assert res2.status == VerificationOutcomeStatus.REVOKED
    print("    [PASS] Flagship product verification vertical slice & revocation propagation verified")

def run_all_product_verification_tests():
    print("=" * 80)
    print("DIGIIN PHASE 32 PRODUCT VERIFICATION TEST MATRIX")
    print("=" * 80)
    test_product_creation_and_opaque_id()
    test_multi_check_verification_valid_and_tampered()
    test_product_lifecycle_status_transitions()
    test_qr_reference_and_public_sanitization()
    test_flagship_vertical_slice_e2e()
    print("=" * 80)
    print("SUCCESS: ALL 5 PRODUCT VERIFICATION TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_product_verification_tests()
