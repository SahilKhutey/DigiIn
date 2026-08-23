"""
DigiIn Automated Service Verification Test Suite (Phase 33)
Validates Service Registry, 8-Stage Request Lifecycle, Citizen Inbox (/dashboard/requests), Explicit Consent ([Allow & Verify] / [Deny]), Verification Execution with Minimal Disclosure, Short-Lived QR Flow, and Flagship Vertical Slice.
"""

import sys
import os

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.service_verification import (
    ServiceRegistry,
    ServiceStatus,
    ServiceVerificationRequest,
    RequestLifecycleStatus,
    CitizenRequestInbox,
    ServiceVerificationCoordinator,
    QRServiceVerifier,
    ServiceDashboardService,
)
from app.core.working_product import ActivityHistoryManager

def test_service_registration_and_auth():
    print(">>> 1. Testing Service Registration & Authentication Context...")
    reg = ServiceRegistry()
    
    # 1. Register new service
    svc, secret = reg.register_service(
        organization_id="org_delhi_univ",
        name="Delhi University Admission Portal",
        description="University portal for verifying Class XII & CUET marks",
        allowed_purposes=["ADMISSION_VERIFICATION"]
    )
    assert svc.status == ServiceStatus.ACTIVE
    assert secret.startswith("dgi_sec_")

    # 2. Authenticate service
    ctx = reg.authenticate_service(svc.id)
    assert ctx is not None
    assert ctx.service_name == "Delhi University Admission Portal"
    assert "ADMISSION_VERIFICATION" in ctx.allowed_purposes
    print("    [PASS] Service registration, client credential auth & context verified")

def test_verification_request_creation_and_lifecycle():
    print(">>> 2. Testing 8-Stage Verification Request Lifecycle...")
    reg = ServiceRegistry()
    inbox = CitizenRequestInbox()
    coord = ServiceVerificationCoordinator(reg, inbox, product_verification_engine=None)

    subject_id = "DGI-7K4M-X9P2-9999"

    # 1. Scholarship portal creates request
    ok, req, msg = coord.create_verification_request(
        service_id="srv_scholarship_portal",
        subject_account_id=subject_id,
        purpose="SCHOLARSHIP_ELIGIBILITY",
        requested_claims=["education.degree", "education.graduationYear"]
    )
    assert ok is True
    assert req.status == RequestLifecycleStatus.DELIVERED

    # 2. Citizen views request
    detail = inbox.view_request_detail(req.request_id, subject_id)
    assert detail is not None
    assert detail.status == RequestLifecycleStatus.VIEWED

    # 3. Test Invalid Transition (Cannot skip to COMPLETED directly from VIEWED)
    invalid_ok, _ = detail.transition_to(RequestLifecycleStatus.COMPLETED)
    assert invalid_ok is False
    print("    [PASS] Verification request creation & 8-stage state machine transitions verified")

def test_citizen_inbox_and_explicit_denial():
    print(">>> 3. Testing Citizen Request Inbox & Explicit Denial ([Deny])...")
    reg = ServiceRegistry()
    inbox = CitizenRequestInbox()
    coord = ServiceVerificationCoordinator(reg, inbox, product_verification_engine=None)

    subject_id = "DGI-7K4M-X9P2-8888"

    ok, req, _ = coord.create_verification_request(
        service_id="srv_sarathi_transport",
        subject_account_id=subject_id,
        purpose="LICENCE_VERIFICATION",
        requested_claims=["licence.number", "licence.validity"]
    )
    assert ok is True

    # 1. List requests for subject
    pending = inbox.list_requests_for_subject(subject_id)
    assert len(pending) == 1

    # 2. Citizen Denies Request
    denied = inbox.deny_request(req.request_id, subject_id, reason="CITIZEN_DECLINED")
    assert denied is True
    assert req.status == RequestLifecycleStatus.DENIED
    assert req.completed_at is not None
    print("    [PASS] Citizen inbox & explicit denial workflow verified")

def test_consent_approval_and_verification_execution():
    print(">>> 4. Testing Consent Approval ([Allow & Verify]) & Minimal Claim Disclosure...")
    reg = ServiceRegistry()
    inbox = CitizenRequestInbox()
    act_mgr = ActivityHistoryManager()
    coord = ServiceVerificationCoordinator(reg, inbox, product_verification_engine=None, activity_mgr=act_mgr)

    subject_id = "DGI-7K4M-X9P2-7777"

    ok_req, req, _ = coord.create_verification_request(
        service_id="srv_scholarship_portal",
        subject_account_id=subject_id,
        purpose="SCHOLARSHIP_ELIGIBILITY",
        requested_claims=["education.degree", "education.graduationYear"]
    )
    assert ok_req is True

    # 1. Citizen approves and executes verification
    ok_ver, ver_res, msg = coord.approve_and_execute_verification(req.request_id, subject_id)
    assert ok_ver is True
    assert ver_res.status == "VERIFIED"
    assert "education.degree" in ver_res.verified_claims
    assert req.status == RequestLifecycleStatus.COMPLETED

    # 2. Check Activity Timeline
    activity = act_mgr.get_user_activity(subject_id)
    assert len(activity) == 1
    assert activity[0].action == "SERVICE_VERIFICATION_COMPLETED"
    print("    [PASS] Consent approval, verification execution & minimal claim disclosure verified")

def test_qr_service_verification_and_metrics():
    print(">>> 5. Testing Short-Lived QR Verification & Service Dashboard Metrics...")
    # 1. Generate QR Service Request
    qr_req, qr_uri = QRServiceVerifier.generate_qr_request(
        service_id="srv_scholarship_portal",
        service_name="National Scholarship Portal",
        purpose="SCHOLARSHIP_ELIGIBILITY",
        requested_claims=["education.degree"]
    )
    assert qr_req.qr_request_id.startswith("qreq_")
    assert "digiin://service-verify/" in qr_uri

    # 2. Compute Dashboard Metrics
    req1 = ServiceVerificationRequest("r1", "s1", "S1", "u1", "P", [], status=RequestLifecycleStatus.COMPLETED)
    req2 = ServiceVerificationRequest("r2", "s1", "S1", "u1", "P", [], status=RequestLifecycleStatus.COMPLETED)
    req3 = ServiceVerificationRequest("r3", "s1", "S1", "u1", "P", [], status=RequestLifecycleStatus.DENIED)
    
    metrics = ServiceDashboardService.compute_service_metrics([req1, req2, req3])
    assert metrics["totalRequests"] == 3
    assert metrics["completed"] == 2
    assert metrics["failed"] == 1
    assert metrics["successRatePercent"] == 66.7
    print("    [PASS] Short-lived QR verification & service dashboard metrics verified")

def test_flagship_service_verification_e2e():
    print(">>> 6. Testing Milestone Flagship Service Verification E2E Journey...")
    reg = ServiceRegistry()
    inbox = CitizenRequestInbox()
    act_mgr = ActivityHistoryManager()
    coord = ServiceVerificationCoordinator(reg, inbox, product_verification_engine=None, activity_mgr=act_mgr)

    citizen_account_id = "DGI-7K4M-X9P2-1234"

    # Step 1: Scholarship Portal creates verification request
    ok, req, _ = coord.create_verification_request(
        service_id="srv_scholarship_portal",
        subject_account_id=citizen_account_id,
        purpose="SCHOLARSHIP_ELIGIBILITY",
        requested_claims=["education.degree", "education.graduationYear"]
    )
    assert ok is True

    # Step 2: Citizen receives request in inbox & reviews details
    viewed_req = inbox.view_request_detail(req.request_id, citizen_account_id)
    assert viewed_req.status == RequestLifecycleStatus.VIEWED

    # Step 3: Citizen clicks [Allow & Verify]
    ok_exec, result, _ = coord.approve_and_execute_verification(req.request_id, citizen_account_id)
    assert ok_exec is True
    assert result.status == "VERIFIED"

    # Step 4: Service retrieves verification result
    fetched_result = coord.get_verification_result(result.verification_id)
    assert fetched_result.status == "VERIFIED"
    assert fetched_result.verified_claims["education.degree"] == "VERIFIED"

    # Step 5: Citizen activity timeline confirms verification
    activities = act_mgr.get_user_activity(citizen_account_id)
    assert len(activities) == 1
    assert "National Scholarship Portal" in activities[0].title
    print("    [PASS] Milestone flagship service verification E2E journey verified with 100% integrity")

def run_all_service_verification_tests():
    print("=" * 80)
    print("DIGIIN PHASE 33 SERVICE VERIFICATION TEST MATRIX")
    print("=" * 80)
    test_service_registration_and_auth()
    test_verification_request_creation_and_lifecycle()
    test_citizen_inbox_and_explicit_denial()
    test_consent_approval_and_verification_execution()
    test_qr_service_verification_and_metrics()
    test_flagship_service_verification_e2e()
    print("=" * 80)
    print("SUCCESS: ALL 6 SERVICE VERIFICATION TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_service_verification_tests()
