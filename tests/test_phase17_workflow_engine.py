"""
DigiIn Automated Workflow & State Machine Test Suite (Phase 17)
Validates authoritative domain state machines, consent scoping, review queues, transactional outbox, and expiration sweeps.
"""

import sys
import os
import time

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.workflow import (
    DocumentState,
    VerificationState,
    ConsentState,
    RequestState,
    ProofState,
    IllegalStateTransitionError,
    DomainWorkflowEngine,
    ConsentEngine,
    ReviewWorkflowEngine,
    ReviewTaskStatus,
    TransactionalOutboxService,
    ExpirationSweeperService,
)

def test_state_machines_and_transition_guards():
    print(">>> 1. Testing Domain State Machines & Guard Enforcements...")
    
    # Document Valid Transition
    doc = {"id": "doc_101", "status": DocumentState.UPLOADING, "version": 1}
    DomainWorkflowEngine.transition_document(doc, "PROCESS")
    assert doc["status"] == DocumentState.PROCESSING
    assert doc["version"] == 2

    DomainWorkflowEngine.transition_document(doc, "COMPLETE")
    assert doc["status"] == DocumentState.READY

    DomainWorkflowEngine.transition_document(doc, "SUBMIT_FOR_REVIEW")
    assert doc["status"] == DocumentState.UNDER_REVIEW

    DomainWorkflowEngine.transition_document(doc, "REJECT")
    assert doc["status"] == DocumentState.REJECTED

    # Document Illegal Transition from Terminal REJECTED -> must raise error
    illegal_caught = False
    try:
        DomainWorkflowEngine.transition_document(doc, "APPROVE")
    except IllegalStateTransitionError:
        illegal_caught = True
    assert illegal_caught is True, "Allowed illegal transition from REJECTED state"

    # Verification Lifecycle
    ver = {"id": "ver_201", "status": VerificationState.CREATED, "version": 1}
    DomainWorkflowEngine.transition_verification(ver, "START")
    assert ver["status"] == VerificationState.PENDING
    
    DomainWorkflowEngine.transition_verification(ver, "COLLECT_EVIDENCE")
    assert ver["status"] == VerificationState.EVIDENCE_COLLECTION

    DomainWorkflowEngine.transition_verification(ver, "EVIDENCE_OK")
    DomainWorkflowEngine.transition_verification(ver, "EVALUATE")
    DomainWorkflowEngine.transition_verification(ver, "PASS")
    assert ver["status"] == VerificationState.VERIFIED
    print("    [PASS] State machines & guard enforcements verified")

def test_claim_level_consent_engine():
    print(">>> 2. Testing Purpose-Bound Claim-Level Consent Engine...")
    engine = ConsentEngine()
    citizen_id = "citizen_rahul_99"
    org_id = "ORG_DELHI_UNIV"
    purpose = "ADMISSION_VERIFICATION"

    # Citizen grants EDUCATION and AGE, but declines RESIDENCE
    consent = engine.create_consent_grant(
        citizen_id=citizen_id,
        organisation_id=org_id,
        request_id="req_901",
        purpose=purpose,
        requested_claims=["EDUCATION", "AGE", "RESIDENCE"],
        granted_claims=["EDUCATION", "AGE"]
    )
    assert consent["status"] == "GRANTED"
    assert "RESIDENCE" in consent["declined_claims"]

    # Check valid consent for granted claims -> PASS
    valid, err, _ = engine.require_valid_consent(
        citizen_id=citizen_id,
        organisation_id=org_id,
        purpose=purpose,
        required_claims=["EDUCATION", "AGE"]
    )
    assert valid is True, f"Failed valid consent check: {err}"

    # Check consent when requiring declined claim (RESIDENCE) -> FAIL
    valid, err, _ = engine.require_valid_consent(
        citizen_id=citizen_id,
        organisation_id=org_id,
        purpose=purpose,
        required_claims=["EDUCATION", "RESIDENCE"]
    )
    assert valid is False
    assert "CONSENT_SCOPE_INSUFFICIENT" in err

    # Check cross-purpose reuse -> FAIL
    valid, err, _ = engine.require_valid_consent(
        citizen_id=citizen_id,
        organisation_id=org_id,
        purpose="MARKETING_PROMOTION",
        required_claims=["EDUCATION"]
    )
    assert valid is False
    assert "CONSENT_REQUIRED" in err
    print("    [PASS] Purpose-bound claim-level consent verified")

def test_review_workflow_and_conflict_of_interest():
    print(">>> 3. Testing Review Workflow & Conflict-of-Interest Guard...")
    engine = ReviewWorkflowEngine()
    task = engine.create_review_task(
        verification_id="ver_401",
        document_id="doc_401",
        citizen_id="citizen_amit_42",
        department="EXAMINATIONS"
    )
    assert task["status"] == ReviewTaskStatus.UNASSIGNED

    # Reviewer attempts to review their OWN document -> DENY (Conflict of interest)
    assigned, err = engine.assign_task(task["id"], reviewer_id="citizen_amit_42")
    assert assigned is False
    assert "CONFLICT_OF_INTEREST" in err

    # Independent officer assigned -> ALLOW
    assigned, err = engine.assign_task(task["id"], reviewer_id="officer_sharma_01")
    assert assigned is True
    assert task["status"] == ReviewTaskStatus.ASSIGNED

    # Complete review
    completed, err = engine.complete_review(task["id"], "officer_sharma_01", "APPROVE", "Legitimate marksheet verified")
    assert completed is True
    assert task["status"] == ReviewTaskStatus.APPROVED
    print("    [PASS] Review workflow & conflict-of-interest checks verified")

def test_transactional_outbox_and_idempotency():
    print(">>> 4. Testing Transactional Outbox & Idempotency Engine...")
    outbox = TransactionalOutboxService()
    
    # Record domain event
    evt = outbox.record_event(
        event_type="PROOF_ISSUED",
        aggregate_type="Proof",
        aggregate_id="prf_777",
        payload={"subject_id": "citizen_99", "claims": ["EDUCATION_VERIFIED"]}
    )
    assert evt.status == "PENDING"

    # Dispatch events
    dispatched = []
    def mock_handler(event_type, agg_id, payload):
        dispatched.append(event_type)

    count = outbox.dispatch_pending_events(mock_handler)
    assert count == 1
    assert "PROOF_ISSUED" in dispatched
    assert evt.status == "PUBLISHED"

    # Test Idempotency
    key = "idem_req_abc_123"
    outbox.save_idempotency(key, {"status": "SUCCESS", "id": "req_888"})
    assert outbox.check_idempotency(key)["id"] == "req_888"
    assert outbox.check_idempotency("non_existent") is None
    print("    [PASS] Transactional outbox & idempotency verified")

def test_expiration_sweeper():
    print(">>> 5. Testing Automated Expiration Sweeper...")
    now = time.time()
    past = now - 100
    future = now + 1000

    docs = [{"id": "d1", "status": "VERIFIED", "expires_at": past}]
    consents = [{"id": "c1", "status": "GRANTED", "expires_at": past}]
    requests = [{"id": "r1", "status": "PENDING_CONSENT", "expires_at": past}]
    proofs = [
        {"id": "p1", "status": "ACTIVE", "expires_at": past},
        {"id": "p2", "status": "ACTIVE", "expires_at": future},
    ]

    counts = ExpirationSweeperService.sweep_expired_records(docs, consents, requests, proofs, now=now)
    assert counts["documents"] == 1
    assert docs[0]["status"] == "EXPIRED"
    assert counts["consents"] == 1
    assert consents[0]["status"] == "EXPIRED"
    assert counts["requests"] == 1
    assert requests[0]["status"] == "EXPIRED"
    assert counts["proofs"] == 1
    assert proofs[0]["status"] == "EXPIRED"
    assert proofs[1]["status"] == "ACTIVE"  # Future proof remains active
    print("    [PASS] Expiration sweeper verified")

def test_provider_unavailable_state():
    print(">>> 6. Testing Provider Unavailable State vs Rejection...")
    ver = {"id": "ver_501", "status": VerificationState.PENDING}
    DomainWorkflowEngine.transition_verification(ver, "PROVIDER_TIMEOUT")
    assert ver["status"] == VerificationState.PROVIDER_UNAVAILABLE, "Incorrect state on provider timeout"

    # Retry transition from PROVIDER_UNAVAILABLE -> PENDING
    DomainWorkflowEngine.transition_verification(ver, "RETRY")
    assert ver["status"] == VerificationState.PENDING
    print("    [PASS] Provider unavailable handling verified")

def run_all_workflow_tests():
    print("=" * 80)
    print("DIGIIN PHASE 17 PRODUCTION WORKFLOW & DETERMINISTIC STATE MACHINE MATRIX")
    print("=" * 80)
    test_state_machines_and_transition_guards()
    test_claim_level_consent_engine()
    test_review_workflow_and_conflict_of_interest()
    test_transactional_outbox_and_idempotency()
    test_expiration_sweeper()
    test_provider_unavailable_state()
    print("=" * 80)
    print("SUCCESS: ALL 6 CORE WORKFLOW & STATE MACHINE TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_workflow_tests()
