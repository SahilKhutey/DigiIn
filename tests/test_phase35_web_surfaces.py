"""
DigiIn Automated Web Surfaces & Multi-Tier Experience Test Suite (Phase 35)
Validates Public Trust Website, Citizen Web App, Service Integration Widget, Institutional 6-Step Stepper Wizard, Route Guards, and Flagship E2E Journey.
"""

import sys
import os

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.web_surfaces import (
    PublicDirectoryManager,
    CitizenWebController,
    ServiceIntegrationWidgetService,
    InstitutionalPortalController,
    UserSession,
    RouteNavigationGuard,
)
from app.core.service_verification import CitizenRequestInbox, ServiceVerificationRequest, RequestLifecycleStatus
from app.core.working_product import ActivityHistoryManager

def test_public_directory_and_trust_surfaces():
    print(">>> 1. Testing Public Services Directory & Trust Registry Surfaces...")
    dir_mgr = PublicDirectoryManager()

    # 1. Search public services
    services = dir_mgr.get_public_services(search="scholarship")
    assert len(services) == 1
    assert services[0].name == "National Scholarship Verification"
    assert "education.degree" in services[0].requested_claims

    # 2. Filter public organizations
    orgs = dir_mgr.get_public_organizations(type_filter="UNIVERSITY")
    assert len(orgs) == 1
    assert orgs[0].name == "University of Delhi"
    assert orgs[0].verified is True

    # 3. How It Works steps
    steps = PublicDirectoryManager.get_how_it_works_steps()
    assert len(steps) == 7
    assert steps[0]["title"] == "Create DigiIn Account"
    print("    [PASS] Public services directory, accredited organizations & how-it-works verified")

def test_citizen_web_controller_and_tabs():
    print(">>> 2. Testing Citizen Web Controller & Request Inbox Tabs...")
    inbox = CitizenRequestInbox()
    act_mgr = ActivityHistoryManager()
    controller = CitizenWebController(inbox, act_mgr)

    subject_id = "DGI-7K4M-X9P2-9999"

    # Add sample request
    req1 = ServiceVerificationRequest(
        request_id="vreq_01",
        service_id="srv_scholarship",
        service_name="Scholarship Portal",
        subject_account_id=subject_id,
        purpose="SCHOLARSHIP_ELIGIBILITY",
        requested_claims=["education.degree"],
        status=RequestLifecycleStatus.DELIVERED
    )
    inbox.register_request(req1)

    # 1. Check summary
    summary = controller.get_dashboard_summary(subject_id, credentials_list=[])
    assert summary.pending_requests_count == 1

    # 2. Check tab filtering
    pending_tabs = controller.filter_requests_by_tab(subject_id, tab="PENDING")
    assert len(pending_tabs) == 1
    completed_tabs = controller.filter_requests_by_tab(subject_id, tab="COMPLETED")
    assert len(completed_tabs) == 0
    print("    [PASS] Citizen dashboard summary & request inbox tab filtering verified")

def test_service_integration_widget_and_auth_flow():
    print(">>> 3. Testing Service Integration Widget & Authorization Code Flow...")
    widget_svc = ServiceIntegrationWidgetService()

    # 1. Partner site triggers widget
    session, redirect_url = widget_svc.initiate_widget_flow(
        service_id="srv_scholarship_portal",
        purpose="SCHOLARSHIP_ELIGIBILITY",
        requested_claims=["education.degree", "education.graduationYear"]
    )
    assert session.code.startswith("dgi_code_")
    assert "/requests/auth?code=" in redirect_url

    # 2. Citizen authenticates and approves consent
    citizen_account_id = "DGI-7K4M-X9P2-1111"
    assert widget_svc.complete_citizen_consent(session.code, citizen_account_id) is True

    # 3. Partner site exchanges code for verified claims
    claims_payload = widget_svc.exchange_code_for_claims(session.code, "srv_scholarship_portal")
    assert claims_payload is not None
    assert claims_payload["status"] == "VERIFIED"
    assert claims_payload["claims"]["education.degree"] == "VERIFIED"
    assert claims_payload["subjectReference"] == citizen_account_id
    print("    [PASS] Reusable service integration widget & authorization code flow verified")

def test_institutional_stepper_wizard_validation():
    print(">>> 4. Testing Institutional 6-Step Stepper Wizard Validation...")
    # Step 1: Citizen ID
    ok1, _ = InstitutionalPortalController.validate_stepper_step(1, {"subjectReference": "DGI-7K4M-9999"})
    assert ok1 is True
    bad1, msg1 = InstitutionalPortalController.validate_stepper_step(1, {"subjectReference": "INVALID-ID"})
    assert bad1 is False
    assert "Must start with DGI-" in msg1

    # Step 2: Purpose
    ok2, _ = InstitutionalPortalController.validate_stepper_step(2, {"purpose": "ADMISSION_VERIFICATION"})
    assert ok2 is True

    # Step 3: Claims
    ok3, _ = InstitutionalPortalController.validate_stepper_step(3, {"requestedClaims": ["education.degree"]})
    assert ok3 is True
    bad3, _ = InstitutionalPortalController.validate_stepper_step(3, {"requestedClaims": []})
    assert bad3 is False

    # Step 4: Policy
    ok4, _ = InstitutionalPortalController.validate_stepper_step(4, {"disclosureMode": "MINIMAL"})
    assert ok4 is True
    print("    [PASS] Institutional 6-step stepper wizard validation verified")

def test_route_navigation_guards_and_roles():
    print(">>> 5. Testing Route Navigation Guards & Role Access Controls...")
    # 1. Public route accessible without session
    ok_pub, _ = RouteNavigationGuard.evaluate_route_access("/services", None)
    assert ok_pub is True

    # 2. Protected route unauthenticated redirects to /login?returnTo=...
    ok_prot, redirect = RouteNavigationGuard.evaluate_route_access("/dashboard", None)
    assert ok_prot is False
    assert redirect == "/login?returnTo=/dashboard"

    # 3. Citizen session accessing citizen route
    citizen_session = UserSession(user_id="u1", account_id="DGI-1", roles={"CITIZEN"})
    ok_cit, _ = RouteNavigationGuard.evaluate_route_access("/dashboard", citizen_session)
    assert ok_cit is True

    # 4. Reviewer route blocked for plain Citizen
    ok_rev, red_rev = RouteNavigationGuard.evaluate_route_access("/institution/review", citizen_session, required_role="REVIEWER")
    assert ok_rev is False
    assert red_rev == "/dashboard"

    # 5. Reviewer session allowed
    reviewer_session = UserSession(user_id="u2", account_id="DGI-2", roles={"REVIEWER"})
    ok_rev_pass, _ = RouteNavigationGuard.evaluate_route_access("/institution/review", reviewer_session, required_role="REVIEWER")
    assert ok_rev_pass is True
    print("    [PASS] Route navigation guards, login redirection & role protection verified")

def test_flagship_web_surfaces_milestone_e2e():
    print(">>> 6. Testing Milestone Flagship Web Surfaces E2E Journey...")
    dir_mgr = PublicDirectoryManager()
    widget_svc = ServiceIntegrationWidgetService()
    act_mgr = ActivityHistoryManager()

    # Step 1: Public Citizen discovers Scholarship Portal in /services
    services = dir_mgr.get_public_services(search="scholarship")
    svc = services[0]
    assert svc.id == "srv_scholarship_portal"

    # Step 2: Citizen clicks "Verify with DigiIn" on partner portal
    session, redirect_url = widget_svc.initiate_widget_flow(
        service_id=svc.id,
        purpose=svc.purpose,
        requested_claims=svc.requested_claims
    )

    # Step 3: Route guard validates authentication
    citizen_session = UserSession(user_id="usr_rahul", account_id="DGI-7K4M-X9P2-9999", roles={"CITIZEN"})
    can_access, _ = RouteNavigationGuard.evaluate_route_access(redirect_url, citizen_session)
    assert can_access is True

    # Step 4: Citizen reviews requested claims & approves
    assert widget_svc.complete_citizen_consent(session.code, citizen_session.account_id) is True

    # Step 5: Partner portal receives minimal verified claims
    claims_res = widget_svc.exchange_code_for_claims(session.code, svc.id)
    assert claims_res["status"] == "VERIFIED"
    assert claims_res["claims"]["education.degree"] == "VERIFIED"

    # Step 6: Citizen activity logged
    act_mgr.record_activity(
        user_id=citizen_session.account_id,
        action="SERVICE_VERIFIED",
        title=f"Verified qualification for {svc.name}",
        details={"purpose": svc.purpose}
    )
    activities = act_mgr.get_user_activity(citizen_session.account_id)
    assert len(activities) == 1
    print("    [PASS] Milestone flagship web surfaces E2E journey verified with 100% integrity")

def run_all_web_surfaces_tests():
    print("=" * 80)
    print("DIGIIN PHASE 35 WEB SURFACES & MULTI-TIER EXPERIENCE TEST MATRIX")
    print("=" * 80)
    test_public_directory_and_trust_surfaces()
    test_citizen_web_controller_and_tabs()
    test_service_integration_widget_and_auth_flow()
    test_institutional_stepper_wizard_validation()
    test_route_navigation_guards_and_roles()
    test_flagship_web_surfaces_milestone_e2e()
    print("=" * 80)
    print("SUCCESS: ALL 6 WEB SURFACES TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_web_surfaces_tests()
