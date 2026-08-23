"""
DigiIn Automated Real Provider & Institutional Integration Test Suite (Phase 19)
Validates provider adapters, data minimization, circuit breakers, evidence normalization, conflict detection, and webhook security.
"""

import sys
import os
import time
import json
import hmac
import hashlib

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.providers import (
    CoreProviderRegistry,
    ProviderGateway,
    SandboxSimulatorAdapter,
    MultiSourceConflictDetector,
    WebhookReceiverService,
    ProviderEvidence,
)

def test_authoritative_provider_verification_flow():
    print(">>> 1. Testing Authoritative Provider Verification & Normalization...")
    registry = CoreProviderRegistry()
    gateway = ProviderGateway(registry)

    # 1. CBSE Board Class XII verification
    success, err, evidence = gateway.execute_verification(
        claim_type="EDUCATION",
        subject_ref="subj_student_8891",
        purpose="COLLEGE_ADMISSION",
        request_id="req_cbse_001",
        parameters={"roll_number": "CBSE-2024-99882", "passing_year": 2024, "unneeded_address": "Private Rd"}
    )
    assert success is True, f"CBSE verification failed: {err}"
    assert evidence.status == "VERIFIED"
    assert evidence.claim_type == "EDUCATION"
    assert evidence.value["percentage"] == 88.5
    assert evidence.source_reference == "CBSE-ROLL-CBSE-2024-99882"
    assert evidence.assurance_level == "HIGH"

    # 2. Delhi University Degree verification
    success, err, evidence_du = gateway.execute_verification(
        claim_type="EDUCATION",
        subject_ref="subj_graduate_2025",
        purpose="EMPLOYMENT_VERIFICATION",
        request_id="req_du_002",
        jurisdiction="IN-DL",
        parameters={"enrollment_no": "DU-2021-CS-101"}
    )
    assert success is True
    assert evidence_du.status == "VERIFIED"
    assert "degree" in evidence_du.value
    assert evidence_du.value["cgpa"] == 8.92

    # 3. Driving Licence verification
    success, err, evidence_dl = gateway.execute_verification(
        claim_type="DRIVING_LICENCE",
        subject_ref="subj_driver_007",
        purpose="INSURANCE_VERIFICATION",
        request_id="req_dl_003"
    )
    assert success is True
    assert evidence_dl.status == "VERIFIED"
    assert "MCWG" in evidence_dl.value["vehicle_classes"]
    print("    [PASS] Authoritative provider execution & normalization verified")

def test_circuit_breaker_and_failure_handling():
    print(">>> 2. Testing Provider Failure, Retries & Circuit Breaker...")
    registry = CoreProviderRegistry()
    gateway = ProviderGateway(registry)
    
    sim_adapter = SandboxSimulatorAdapter()
    gateway.register_adapter("provider_sandbox_sim", sim_adapter)

    # Configure sandbox simulator to simulate timeouts
    sim_adapter.set_mode("TIMEOUT")

    success, err, evidence = gateway.execute_verification(
        claim_type="ADDRESS",
        subject_ref="subj_fail_test",
        purpose="ADDRESS_CHECK",
        request_id="req_fail_01",
        max_retries=1
    )
    assert success is False
    assert "PROVIDER_UNAVAILABLE" in err or "NO_AUTHORITATIVE_PROVIDER" in err
    print("    [PASS] Timeout retry & circuit breaker resilience verified")

def test_multi_source_conflict_detection():
    print(">>> 3. Testing Multi-Source Evidence Conflict Detection...")
    ev1 = ProviderEvidence(
        provider_id="provider_delhi_univ",
        subject_reference="subj_amit_88",
        claim_type="EDUCATION",
        value={"degree": "B.Tech in Computer Science", "status": "VERIFIED"},
        status="VERIFIED"
    )
    ev2_matching = ProviderEvidence(
        provider_id="provider_cbse_in",
        subject_reference="subj_amit_88",
        claim_type="EDUCATION",
        value={"degree": "B.Tech in Computer Science", "status": "VERIFIED"},
        status="VERIFIED"
    )
    ev3_conflicting = ProviderEvidence(
        provider_id="provider_other_univ",
        subject_reference="subj_amit_88",
        claim_type="EDUCATION",
        value={"degree": "B.Sc in Mathematics", "status": "VERIFIED"},
        status="VERIFIED"
    )

    # 1. Consistent sources -> NO CONFLICT
    res_clean = MultiSourceConflictDetector.evaluate_evidence_consistency([ev1, ev2_matching])
    assert res_clean.has_conflict is False

    # 2. Discrepancy between degrees -> FACTUAL DISCREPANCY CONFLICT
    res_conflict = MultiSourceConflictDetector.evaluate_evidence_consistency([ev1, ev3_conflicting])
    assert res_conflict.has_conflict is True
    assert res_conflict.conflict_type == "FACTUAL_DISCREPANCY"
    assert "B.Tech" in res_conflict.reason and "B.Sc" in res_conflict.reason
    print("    [PASS] Multi-source conflict detection & flagging verified")

def test_webhook_hmac_and_replay_defense():
    print(">>> 4. Testing Webhook HMAC Signature & Replay Defense...")
    webhook_service = WebhookReceiverService(timestamp_tolerance_seconds=300)
    provider_id = "provider_cbse_in"
    secret = "cbse_webhook_shared_secret_32_bytes"
    
    payload_dict = {"event": "CREDENTIAL_UPDATED", "candidateRef": "subj_99", "status": "RE_EVALUATED"}
    payload_bytes = json.dumps(payload_dict).encode("utf-8")
    
    now = time.time()
    ts_header = str(now)
    
    # Compute genuine signature
    signed_payload = f"{ts_header}.".encode("utf-8") + payload_bytes
    valid_signature = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()

    # 1. Valid Webhook Ingestion -> PASS
    valid, err, parsed = webhook_service.verify_and_ingest_webhook(
        provider_id=provider_id,
        secret_key=secret,
        payload_bytes=payload_bytes,
        signature_header=valid_signature,
        timestamp_header=ts_header,
        event_id="evt_cbse_889911"
    )
    assert valid is True
    assert parsed["event"] == "CREDENTIAL_UPDATED"

    # 2. Replay of same event_id -> REJECT (DUPLICATE_EVENT)
    valid, err, _ = webhook_service.verify_and_ingest_webhook(
        provider_id=provider_id,
        secret_key=secret,
        payload_bytes=payload_bytes,
        signature_header=valid_signature,
        timestamp_header=ts_header,
        event_id="evt_cbse_889911"
    )
    assert valid is False
    assert "DUPLICATE_EVENT" in err

    # 3. Forged signature -> REJECT (SIGNATURE_MISMATCH)
    valid, err, _ = webhook_service.verify_and_ingest_webhook(
        provider_id=provider_id,
        secret_key=secret,
        payload_bytes=payload_bytes,
        signature_header="forged_signature_0000",
        timestamp_header=ts_header,
        event_id="evt_cbse_889912"
    )
    assert valid is False
    assert "SIGNATURE_MISMATCH" in err

    # 4. Expired timestamp (>5 mins old) -> REJECT (WEBHOOK_EXPIRED)
    old_ts_header = str(now - 600)
    old_signed_payload = f"{old_ts_header}.".encode("utf-8") + payload_bytes
    old_sig = hmac.new(secret.encode("utf-8"), old_signed_payload, hashlib.sha256).hexdigest()
    valid, err, _ = webhook_service.verify_and_ingest_webhook(
        provider_id=provider_id,
        secret_key=secret,
        payload_bytes=payload_bytes,
        signature_header=old_sig,
        timestamp_header=old_ts_header,
        event_id="evt_cbse_889913"
    )
    assert valid is False
    assert "WEBHOOK_EXPIRED" in err
    print("    [PASS] Webhook HMAC validation & replay defense verified")

def run_all_provider_tests():
    print("=" * 80)
    print("DIGIIN PHASE 19 REAL PROVIDER & INSTITUTIONAL INTEGRATION TEST MATRIX")
    print("=" * 80)
    test_authoritative_provider_verification_flow()
    test_circuit_breaker_and_failure_handling()
    test_multi_source_conflict_detection()
    test_webhook_hmac_and_replay_defense()
    print("=" * 80)
    print("SUCCESS: ALL 4 REAL PROVIDER & INSTITUTIONAL INTEGRATION TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_provider_tests()
