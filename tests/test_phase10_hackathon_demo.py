"""Phase 10 — Hackathon Demonstration & Showcase Test Suite.

Validates:
  1. Demo Persona registry & multi-role actor lookup.
  2. Verifiable QR Proof Generator (compression, encoding, ASCII rendering & round-trip decoding).
  3. Judge Scorecard compiler & maturity telemetry.
  4. 10-Milestone Flagship Hackathon Scenario execution.
  5. Hackathon Demo API endpoints (/api/v1/demo/*).
"""

from __future__ import annotations

import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "services" / "api"))
sys.path.insert(0, str(root_dir))

from fastapi.testclient import TestClient

from app.core.demo import DEMO_PERSONAS, flagship_demo, judge_scorecard, qr_generator
from app.db.session import init_db
from app.main import app

init_db()
client = TestClient(app)


def test_demo_personas():
    print(">>> 10.1 Demo Personas Registry...")
    personas = flagship_demo.get_personas()
    assert len(personas) >= 4

    roles = {p["role"] for p in personas}
    assert "CITIZEN" in roles
    assert "OFFICER" in roles
    assert "REVIEWER" in roles
    assert "ADMIN" in roles

    citizen = DEMO_PERSONAS["citizen"]
    assert citizen.name == "Rahul Sharma"
    assert citizen.account_id == "DIN-2026-IND-7782"

    print("    [PASS] All 4 demonstration personas verified (Citizen, Officer, Reviewer, Operator)")


def test_qr_generator_roundtrip():
    print(">>> 10.2 Verifiable QR Code Encoding & Decoding...")

    mock_proof = {
        "proofId": "prf_test_7788",
        "issuer": "did:digiin:authority:root",
        "subject": "DIN-2026-IND-7782",
        "proofType": "EDUCATION_VERIFIED",
        "purpose": "SCHOLARSHIP_CHECK",
        "claims": [{"type": "EDUCATION", "value": {"education_verified": True}}],
        "signature": "simulated_ed25519_sig_abc123",
    }

    # 1. Encode
    qr_payload = qr_generator.encode_proof_to_qr_payload(mock_proof)
    assert qr_payload.startswith("digiin://verify/v1/")
    assert len(qr_payload) < 500  # Compact compressed payload

    # 2. Decode
    decoded = qr_generator.decode_qr_payload_to_proof(qr_payload)
    assert decoded["proofId"] == mock_proof["proofId"]
    assert decoded["claims"] == mock_proof["claims"]
    assert decoded["signature"] == mock_proof["signature"]

    # 3. ASCII QR Visual
    ascii_qr = qr_generator.generate_ascii_qr("CBSE 2026", qr_payload)
    assert "[SOVEREIGN VERIFICATION QR]" in ascii_qr
    assert "+" in ascii_qr

    print("    [PASS] QR proof compression, URL-safe encoding, ASCII rendering, and lossless decoding verified")


def test_judge_scorecard():
    print(">>> 10.3 Judge Evaluation Scorecard Compilation...")

    scorecard = judge_scorecard.compile_scorecard()
    assert scorecard["project"]["name"] == "DigiLocker X (DigiIn)"
    assert scorecard["project"]["maturity_phases_completed"] == 10
    assert scorecard["operational_resilience"]["slo_overall_status"] == "COMPLIANT"
    assert "encryption_at_rest" in scorecard["security_and_privacy_guarantees"]
    assert len(scorecard["trust_network_and_issuers"]["active_providers"]) >= 3
    assert scorecard["test_matrix_status"]["pass_rate_pct"] == 100.0

    print("    [PASS] Complete judge evaluation scorecard compiled with real-time operational telemetry")


def test_flagship_scenario_execution():
    print(">>> 10.4 10-Milestone Flagship Demonstration Scenario...")

    result = flagship_demo.run_flagship_scenario()
    assert result["status"] == "ALL_STEPS_SUCCESSFUL"
    assert result["total_steps"] == 10
    assert result["total_execution_time_ms"] > 0.0

    step_titles = [s["title"] for s in result["steps"]]
    assert "Persona Authentication & Zero-Trust Session" in step_titles[0]
    assert "Document Ingestion & Envelope Encryption at Rest" in step_titles[1]
    assert "AI OCR Intelligence & Document Classification" in step_titles[2]
    assert "Authoritative External Integration Verification" in step_titles[3]
    assert "Purpose-Bound Verification Request & Citizen Consent" in step_titles[4]
    assert "Minimal Selective Disclosure & Ed25519 Cryptographic Proof" in step_titles[5]
    assert "Verifiable QR Proof Packaging" in step_titles[6]
    assert "Department Cryptographic Proof Verification" in step_titles[7]
    assert "Tamper-Evident SHA-256 Linked Audit Chain" in step_titles[8]
    assert "Live Observability Metrics & Judge Scorecard Export" in step_titles[9]

    print(f"    [PASS] Flagship demonstration scenario completed in {result['total_execution_time_ms']}ms with 10/10 steps PASS")


def test_demo_api_endpoints():
    print(">>> 10.5 Hackathon Demo API Endpoints (/api/v1/demo/*)...")

    # 1. Personas
    resp_personas = client.get("/api/v1/demo/personas")
    assert resp_personas.status_code == 200
    assert len(resp_personas.json()) >= 4

    # 2. Scorecard
    resp_scorecard = client.get("/api/v1/demo/scorecard")
    assert resp_scorecard.status_code == 200
    assert resp_scorecard.json()["project"]["maturity_phases_completed"] == 10

    # 3. QR Encode
    sample_proof = {"proofId": "prf_api_01", "proofType": "MARKSHEET", "signature": "sig_123"}
    resp_encode = client.post("/api/v1/demo/qr/encode", json=sample_proof)
    assert resp_encode.status_code == 200
    encode_data = resp_encode.json()
    assert "qr_payload" in encode_data

    # 4. QR Decode
    resp_decode = client.post("/api/v1/demo/qr/decode", json={"qr_payload": encode_data["qr_payload"]})
    assert resp_decode.status_code == 200
    assert resp_decode.json()["proof"]["proofId"] == "prf_api_01"

    # 5. Flagship Scenario Run
    resp_scenario = client.post("/api/v1/demo/run-scenario")
    assert resp_scenario.status_code == 200
    assert resp_scenario.json()["status"] == "ALL_STEPS_SUCCESSFUL"

    print("    [PASS] All 5 hackathon demonstration API endpoints verified (200 OK)")


if __name__ == "__main__":
    print("=" * 80)
    print("DIGIIN PHASE 10 — HACKATHON DEMONSTRATION & EVALUATION TEST SUITE")
    print("=" * 80)

    test_demo_personas()
    test_qr_generator_roundtrip()
    test_judge_scorecard()
    test_flagship_scenario_execution()
    test_demo_api_endpoints()

    print()
    print("=" * 80)
    print("SUCCESS: ALL PHASE 10 HACKATHON DEMO & EVALUATION TESTS PASSED!")
    print("=" * 80)
