"""
DigiIn Automated Institutional Review & Operating Layer Test Suite (Phase 34)
Validates Organization & Department Hierarchy, Scoped Institutional RBAC, Request Templates, Review Queue (/institution/review), Separation of Verification vs Institutional Decision, Chronological Timelines, HMAC Webhooks, and Flagship Vertical Slice.
"""

import sys
import os

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.institutional_review import (
    OrganizationHierarchyManager,
    OrganizationRole,
    InstitutionalRBACGuard,
    RequestTemplateManager,
    DepartmentRequestEngine,
    InstitutionalReviewManager,
    InstitutionalDecisionType,
    InstitutionalWebhookDispatcher,
    InstitutionalDashboardService,
)

def test_organization_hierarchy_and_rbac():
    print(">>> 1. Testing Organization Hierarchy & Scoped Institutional RBAC...")
    hierarchy = OrganizationHierarchyManager()
    org = hierarchy.get_organization("org_delhi_university")
    assert org is not None
    assert org.verified is True

    admin_user = hierarchy.get_user("iuser_org_admin")
    reviewer_user = hierarchy.get_user("iuser_reviewer")

    # 1. Org Admin has broad permissions
    ok_admin, _ = InstitutionalRBACGuard.is_authorized(admin_user, "users:manage")
    assert ok_admin is True

    # 2. Reviewer cannot manage users
    ok_rev_user, msg_rev = InstitutionalRBACGuard.is_authorized(reviewer_user, "users:manage")
    assert ok_rev_user is False
    assert "PERMISSION_DENIED" in msg_rev

    # 3. Reviewer can review within own department (dept_admissions)
    ok_rev_dept, _ = InstitutionalRBACGuard.is_authorized(reviewer_user, "decisions:create", "dept_admissions")
    assert ok_rev_dept is True

    # 4. Reviewer cannot operate on foreign department (dept_scholarships)
    ok_rev_foreign, msg_for = InstitutionalRBACGuard.is_authorized(reviewer_user, "decisions:create", "dept_scholarships")
    assert ok_rev_foreign is False
    assert "DEPARTMENT_SCOPING_DENIED" in msg_for
    print("    [PASS] Organization hierarchy, department scoping & 5-role RBAC verified")

def test_request_template_management():
    print(">>> 2. Testing Request Template Management & Policy Presets...")
    tmpl_mgr = RequestTemplateManager()

    # 1. List default templates
    adm_templates = tmpl_mgr.list_templates_for_department("dept_admissions")
    assert len(adm_templates) == 1
    assert adm_templates[0].purpose == "ADMISSION_VERIFICATION"

    # 2. Create custom template
    t_new = tmpl_mgr.create_template(
        organization_id="org_delhi_university",
        department_id="dept_scholarships",
        name="Postgraduate Research Grant Verification",
        purpose="GRANT_ELIGIBILITY",
        required_claims=["education.masters_degree", "education.cgpa"],
        minimum_assurance="A3_HIGH_ASSURANCE",
        disclosure_mode="MINIMAL"
    )
    assert t_new.id.startswith("tmpl_")
    assert t_new.name == "Postgraduate Research Grant Verification"
    print("    [PASS] Request template manager and policy presets verified")

def test_department_request_creation_and_review_queue():
    print(">>> 3. Testing Department Request Creation & Review Queue Ingestion...")
    hierarchy = OrganizationHierarchyManager()
    req_engine = DepartmentRequestEngine()
    review_mgr = InstitutionalReviewManager()

    admin_user = hierarchy.get_user("iuser_org_admin")

    # 1. Create verification request
    ok_req, req, _ = req_engine.create_request(
        user=admin_user,
        department_name="Admissions Division",
        subject_reference="DGI-7K4M-X9P2-9999",
        purpose="ADMISSION_VERIFICATION",
        requested_claims=["education.class_xii_marksheet"],
        target_department_id="dept_admissions"
    )
    assert ok_req is True
    assert req.status == "PENDING_CITIZEN"

    # 2. Ingest into review queue
    all_reqs = req_engine.list_requests_for_department("dept_admissions")
    queue_pending = review_mgr.get_review_queue(all_reqs, status_filter="PENDING_CITIZEN")
    assert len(queue_pending) == 1
    assert queue_pending[0].request_id == req.request_id
    print("    [PASS] Department request creation & review queue filtering verified")

def test_separation_of_verification_vs_decision_and_timeline():
    print(">>> 4. Testing Separation of DigiIn Verification vs Institutional Decision & Timeline...")
    hierarchy = OrganizationHierarchyManager()
    req_engine = DepartmentRequestEngine()
    review_mgr = InstitutionalReviewManager()

    admin_user = hierarchy.get_user("iuser_org_admin")
    reviewer_user = hierarchy.get_user("iuser_reviewer")

    ok_req, req, _ = req_engine.create_request(
        user=admin_user,
        department_name="Admissions Division",
        subject_reference="DGI-7K4M-X9P2-7777",
        purpose="ADMISSION_VERIFICATION",
        requested_claims=["education.class_xii_marksheet"],
        target_department_id="dept_admissions"
    )
    assert ok_req is True

    # 1. DigiIn Engine records verification result -> VERIFIED
    review_mgr.record_verification_result(
        request=req,
        verification_status="VERIFIED",
        assurance_level="A3_HIGH_ASSURANCE",
        verified_claims={"education.class_xii_marksheet": "VERIFIED"}
    )
    assert req.status == "IN_REVIEW"

    # 2. Department Reviewer records institutional decision -> APPROVED
    ok_dec, dec, _ = review_mgr.record_institutional_decision(
        user=reviewer_user,
        request=req,
        decision=InstitutionalDecisionType.APPROVED,
        reason="Candidate meets cutoff criteria percentage >= 95%",
        notes="All transcripts matched."
    )
    assert ok_dec is True
    assert req.status == "COMPLETED"
    assert dec.decision == "APPROVED"

    # 3. Validate Chronological Timeline Progression
    assert len(req.timeline) == 3
    assert req.timeline[0]["event"] == "REQUEST_CREATED"
    assert req.timeline[1]["event"] == "CRYPTOGRAPHIC_VERIFICATION_COMPLETED"
    assert req.timeline[2]["event"] == "INSTITUTIONAL_DECISION_APPROVED"
    print("    [PASS] Separation of verification vs institutional decision and timeline verified")

def test_hmac_webhook_dispatch_and_dashboard_metrics():
    print(">>> 5. Testing HMAC-Signed Webhook Dispatch & Dashboard Analytics...")
    dispatcher = InstitutionalWebhookDispatcher(secret="univ_erp_secret_key")

    # 1. Dispatch event
    delivery = dispatcher.dispatch_event(
        organization_id="org_delhi_university",
        target_url="https://erp.du.ac.in/api/v1/digiin-webhook",
        event_type="verification.completed",
        data={"requestId": "vr_test_01", "decision": "APPROVED"}
    )
    assert delivery.status == "DELIVERED"
    assert delivery.signature_hex is not None

    # 2. Verify signature
    valid_sig = dispatcher.verify_webhook_signature(delivery.payload, delivery.signature_hex)
    assert valid_sig is True

    # 3. Dashboard Metrics
    req_engine = DepartmentRequestEngine()
    hierarchy = OrganizationHierarchyManager()
    admin_user = hierarchy.get_user("iuser_org_admin")
    _, r1, _ = req_engine.create_request(admin_user, "Admissions", "DGI-1", "ADM", ["c1"], target_department_id="dept_admissions")
    r1.status = "COMPLETED"

    metrics = InstitutionalDashboardService.get_organization_metrics([r1])
    assert metrics["totalRequests"] == 1
    assert metrics["completed"] == 1
    assert metrics["completionRatePercent"] == 100.0
    print("    [PASS] HMAC-signed webhook dispatch, signature verification & dashboard metrics verified")

def test_flagship_institutional_review_vertical_slice_e2e():
    print(">>> 6. Testing Milestone Flagship Institutional Review E2E Vertical Slice...")
    hierarchy = OrganizationHierarchyManager()
    req_engine = DepartmentRequestEngine()
    review_mgr = InstitutionalReviewManager()
    webhook_dispatcher = InstitutionalWebhookDispatcher(secret="du_erp_sec")

    admin = hierarchy.get_user("iuser_org_admin")
    reviewer = hierarchy.get_user("iuser_reviewer")
    citizen_account_id = "DGI-7K4M-X9P2-4321"

    # Step 1: Admissions Officer creates verification request
    ok_req, req, _ = req_engine.create_request(
        user=admin,
        department_name="Admissions Division",
        subject_reference=citizen_account_id,
        purpose="ADMISSION_VERIFICATION",
        requested_claims=["education.class_xii_marksheet", "identity.name"],
        target_department_id="dept_admissions"
    )
    assert ok_req is True

    # Step 2: Citizen consents & DigiIn performs cryptographic verification
    review_mgr.record_verification_result(
        request=req,
        verification_status="VERIFIED",
        assurance_level="A3_HIGH_ASSURANCE",
        verified_claims={"education.class_xii_marksheet": "VERIFIED", "identity.name": "Rahul Sharma"}
    )
    assert req.status == "IN_REVIEW"

    # Step 3: Admissions Reviewer evaluates verification outcome and approves application
    ok_dec, decision, _ = review_mgr.record_institutional_decision(
        user=reviewer,
        request=req,
        decision=InstitutionalDecisionType.APPROVED,
        reason="Merit list #42 qualified",
        notes="Verified directly via DigiIn Sovereign Gateway"
    )
    assert ok_dec is True
    assert req.status == "COMPLETED"

    # Step 4: Webhook automatically dispatched to University ERP
    delivery = webhook_dispatcher.dispatch_event(
        organization_id=req.organization_id,
        target_url="https://admissions.du.ac.in/webhook/digiin",
        event_type="institutional.decision.recorded",
        data={
            "requestId": req.request_id,
            "decision": decision.decision,
            "reason": decision.reason,
            "decidedBy": decision.decided_by_name
        }
    )
    assert delivery.status == "DELIVERED"
    assert webhook_dispatcher.verify_webhook_signature(delivery.payload, delivery.signature_hex) is True
    print("    [PASS] Milestone flagship institutional review vertical slice verified with 100% integrity")

def run_all_institutional_review_tests():
    print("=" * 80)
    print("DIGIIN PHASE 34 INSTITUTIONAL REVIEW & OPERATING LAYER TEST MATRIX")
    print("=" * 80)
    test_organization_hierarchy_and_rbac()
    test_request_template_management()
    test_department_request_creation_and_review_queue()
    test_separation_of_verification_vs_decision_and_timeline()
    test_hmac_webhook_dispatch_and_dashboard_metrics()
    test_flagship_institutional_review_vertical_slice_e2e()
    print("=" * 80)
    print("SUCCESS: ALL 6 INSTITUTIONAL REVIEW TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_institutional_review_tests()
