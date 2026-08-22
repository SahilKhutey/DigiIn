"""Security, Anti-Piracy, and Anti-Counterfeit Test Suite.

Verifies:
1. Cryptographic digital watermarking & tamper detection
2. Anti-replay nonce tracking and replay attack prevention
3. Fraudulent/counterfeit document fingerprint detection
4. Anti-brute-force rate limiting and request throttling
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add services and repo root to sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "services" / "api"))
sys.path.insert(0, str(root_dir))

from app.core.anti_piracy import (
    AntiReplayNonceManager,
    CounterfeitFingerprintRegistry,
    generate_digital_watermark,
    verify_digital_watermark,
)
from app.core.rate_limit import InMemoryRateLimiter


def test_digital_watermarking_and_tamper_proofing():
    doc_id = "doc_cbse_senior_2026"
    owner_id = "subj_rahul_sharma_99"

    # 1. Generate Watermark
    wm = generate_digital_watermark(document_id=doc_id, owner_subject_id=owner_id)
    assert wm["documentId"] == doc_id
    assert wm["ownerSubjectId"] == owner_id
    assert "antiPiracySeal" in wm

    # 2. Verify Valid Watermark
    assert verify_digital_watermark(wm) is True

    # 3. Tamper with Watermark (change ownerSubjectId)
    tampered_wm = dict(wm)
    tampered_wm["ownerSubjectId"] = "subj_pirate_attacker_00"
    assert verify_digital_watermark(tampered_wm) is False


def test_anti_replay_nonce_protection():
    nonce_mgr = AntiReplayNonceManager(ttl_seconds=10)

    # 1. Generate Nonce
    nonce = nonce_mgr.generate_nonce()
    assert nonce.startswith("nonce_")

    # 2. Consume Nonce (first use -> OK)
    assert nonce_mgr.consume_nonce(nonce) is True

    # 3. Replay Nonce (second use -> REJECTED)
    assert nonce_mgr.consume_nonce(nonce) is False


def test_counterfeit_fingerprint_registry():
    registry = CounterfeitFingerprintRegistry()

    # Known blacklisted hash
    fake_hash = "deadbeef00000000000000000000000000000000000000000000000000000000"
    assert registry.is_flagged_counterfeit(fake_hash) is True

    # Legitimate hash
    legit_hash = "11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff"
    assert registry.is_flagged_counterfeit(legit_hash) is False

    # Flag new pirated document
    registry.flag_counterfeit(legit_hash, reason="REPORTED_STOLEN_CREDENTIAL")
    assert registry.is_flagged_counterfeit(legit_hash) is True


def test_rate_limiting_and_brute_force_throttling():
    limiter = InMemoryRateLimiter(max_requests=3, window_seconds=60)
    user_key = "user_brute_force_test"

    # 1. First 3 requests -> Allowed
    ok1, rem1 = limiter.is_allowed(user_key)
    assert ok1 is True
    assert rem1 == 2

    ok2, rem2 = limiter.is_allowed(user_key)
    assert ok2 is True
    assert rem2 == 1

    ok3, rem3 = limiter.is_allowed(user_key)
    assert ok3 is True
    assert rem3 == 0

    # 2. 4th request -> Blocked
    ok4, rem4 = limiter.is_allowed(user_key)
    assert ok4 is False
    assert rem4 == 0

    # 3. Reset
    limiter.reset(user_key)
    ok5, rem5 = limiter.is_allowed(user_key)
    assert ok5 is True


if __name__ == "__main__":
    test_digital_watermarking_and_tamper_proofing()
    test_anti_replay_nonce_protection()
    test_counterfeit_fingerprint_registry()
    test_rate_limiting_and_brute_force_throttling()
    print("SUCCESS: ALL SECURITY AND ANTI-PIRACY TESTS PASSED!")
