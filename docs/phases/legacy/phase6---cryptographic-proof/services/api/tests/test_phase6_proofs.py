from app.crypto.proofs import generate_keypair, sign_proof, verify_proof


def make_proof():
    private, public = generate_keypair()
    proof = sign_proof(
        proof_id="PRF-1",
        issuer="digiin",
        audience="dept-scholarship",
        nonce="REQ-NONCE",
        claims={"income_band": "eligible"},
        key_id="key-1",
        private_key=private,
        expires_at=2_000_000_000,
        issued_at=1_900_000_000,
    )
    return proof, public


def test_valid_proof_verifies():
    proof, public = make_proof()
    assert verify_proof(
        proof,
        public_key=public,
        expected_issuer="digiin",
        expected_audience="dept-scholarship",
        expected_nonce="REQ-NONCE",
        now=1_900_000_100,
    )


def test_tampered_claim_fails():
    proof, public = make_proof()
    tampered = proof.__class__(**{**proof.__dict__, "claims": {"income_band": "not-eligible"}})
    assert not verify_proof(
        tampered,
        public_key=public,
        expected_issuer="digiin",
        expected_audience="dept-scholarship",
        expected_nonce="REQ-NONCE",
        now=1_900_000_100,
    )


def test_wrong_audience_fails():
    proof, public = make_proof()
    assert not verify_proof(
        proof,
        public_key=public,
        expected_issuer="digiin",
        expected_audience="other-department",
        expected_nonce="REQ-NONCE",
        now=1_900_000_100,
    )


def test_wrong_nonce_fails():
    proof, public = make_proof()
    assert not verify_proof(
        proof,
        public_key=public,
        expected_issuer="digiin",
        expected_audience="dept-scholarship",
        expected_nonce="OTHER",
        now=1_900_000_100,
    )


def test_expired_proof_fails():
    proof, public = make_proof()
    assert not verify_proof(
        proof,
        public_key=public,
        expected_issuer="digiin",
        expected_audience="dept-scholarship",
        expected_nonce="REQ-NONCE",
        now=2_000_000_001,
    )
