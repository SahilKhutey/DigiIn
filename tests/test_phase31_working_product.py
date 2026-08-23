"""
DigiIn Automated Working Product & User Request Handling Test Suite (Phase 31)
Validates Standard Request Pipeline, Idempotency, Flow 1 (Upload/Verify), Flow 2 (Institutional Request/Consent), Flow 3 (Credential Issuance/Presentation), and Error Shielding.
"""

import sys
import os

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.working_product import (
    DigiInRequest,
    DigiInResponse,
    IdempotencyManager,
    AuthContext,
    AuthorizationGuard,
    UserActionTypes,
    UserActionRouter,
    DocumentVerificationWorkflow,
    InstitutionalConsentWorkflow,
    CredentialPresentationWorkflow,
    ActivityHistoryManager,
    NotificationManager,
    DigiInError,
    ErrorSanitizer,
)

def create_sample_auth_context(user_id: str = "usr_rahul_99", roles=None, permissions=None) -> AuthContext:
    return AuthContext(
        user_id=user_id,
        account_id=f"DGI-7K4M-X9P2-9999",
        roles=roles or ["CITIZEN"],
        organization_ids=[],
        permissions=set(permissions or ["document:upload", "document:read", "verification:create", "consent:create", "credential:present"]),
        session_id="sess_live_12345"
    )

def test_request_envelope_and_idempotency():
    print(">>> 1. Testing Standard Request Envelope & Idempotency Pipeline...")
    idemp_mgr = IdempotencyManager()

    # 1. Create Request
    req = DigiInRequest.create(
        actor_type="USER",
        actor_id="usr_rahul_99",
        action=UserActionTypes.UPLOAD_DOCUMENT,
        payload={"filename": "Degree.pdf", "mimeType": "application/pdf"},
        idempotency_key="idemp_upload_key_001"
    )
    assert req.request_id.startswith("req_")

    # 2. Check initial idempotency -> None
    assert idemp_mgr.check_and_get("idemp_upload_key_001") is None

    # 3. Cache response
    resp = DigiInResponse.ok(req.request_id, {"documentId": "doc_123"})
    idemp_mgr.record_response("idemp_upload_key_001", resp)

    # 4. Repeated submission returns cached response
    cached = idemp_mgr.check_and_get("idemp_upload_key_001")
    assert cached is not None
    assert cached.data["documentId"] == "doc_123"
    print("    [PASS] Standard request envelope and idempotency pipeline verified")

def test_flow1_document_upload_and_verification():
    print(">>> 2. Testing Flow 1: Document Upload & Verification Lifecycle...")
    act_mgr = ActivityHistoryManager()
    notif_mgr = NotificationManager()
    doc_workflow = DocumentVerificationWorkflow(act_mgr, notif_mgr)
    auth = create_sample_auth_context()

    # 1. Upload Document
    upload_req = DigiInRequest.create(
        actor_type="USER",
        actor_id=auth.user_id,
        action=UserActionTypes.UPLOAD_DOCUMENT,
        payload={"filename": "Class_XII_Marksheet.pdf", "mimeType": "application/pdf", "sizeBytes": 2048}
    )
    upload_res = doc_workflow.handle_upload_document(upload_req, auth)
    assert upload_res.success is True
    doc_id = upload_res.data["documentId"]
    assert upload_res.data["status"] == "PENDING"

    # 2. Request Verification
    verify_req = DigiInRequest.create(
        actor_type="USER",
        actor_id=auth.user_id,
        action=UserActionTypes.REQUEST_VERIFICATION,
        payload={"documentId": doc_id}
    )
    verify_res = doc_workflow.handle_request_verification(verify_req, auth)
    assert verify_res.success is True
    assert verify_res.data["status"] == "VERIFIED"

    # 3. Check Activity History & In-App Notifications
    activities = act_mgr.get_user_activity(auth.user_id)
    assert len(activities) == 2
    assert activities[0].action == "DOCUMENT_UPLOADED"
    assert activities[1].action == "VERIFICATION_COMPLETED"

    notifications = notif_mgr.get_unread_notifications(auth.user_id)
    assert len(notifications) == 2
    print("    [PASS] Flow 1: Document upload, authoritative verification & activity logs verified")

def test_flow2_institutional_request_and_consent():
    print(">>> 3. Testing Flow 2: Institutional Verification Request & Citizen Consent...")
    act_mgr = ActivityHistoryManager()
    notif_mgr = NotificationManager()
    consent_workflow = InstitutionalConsentWorkflow(act_mgr, notif_mgr)
    auth = create_sample_auth_context()

    # 1. Scholarship Portal creates verification request
    vreq = consent_workflow.create_verification_request(
        verifier_id="ver_scholarship_portal",
        verifier_name="National Scholarship Portal",
        subject_id=auth.user_id,
        purpose="SCHOLARSHIP_ELIGIBILITY",
        requested_claims=["education.degree", "education.marksheet"]
    )
    assert vreq.status == "PENDING"
    assert len(notif_mgr.get_unread_notifications(auth.user_id)) == 1

    # 2. Citizen approves consent
    approve_req = DigiInRequest.create(
        actor_type="USER",
        actor_id=auth.user_id,
        action=UserActionTypes.APPROVE_CONSENT,
        payload={"verificationRequestId": vreq.request_id}
    )
    approve_res = consent_workflow.handle_approve_consent(approve_req, auth)
    assert approve_res.success is True
    assert approve_res.data["status"] == "APPROVED"
    assert approve_res.data["proofToken"].startswith("prf_token_")
    print("    [PASS] Flow 2: Institutional verification request & citizen consent verified")

def test_flow3_credential_presentation_and_revocation():
    print(">>> 4. Testing Flow 3: Credential Issuance, Presentation & Revocation...")
    act_mgr = ActivityHistoryManager()
    notif_mgr = NotificationManager()
    cred_workflow = CredentialPresentationWorkflow(act_mgr, notif_mgr)
    auth = create_sample_auth_context()

    # 1. University issues credential
    cred = cred_workflow.issue_credential(
        issuer_id="iss_delhi_university",
        subject_id=auth.user_id,
        credential_type="education.degree",
        claims={"degree": "B.Tech Computer Science", "year": 2025}
    )
    assert cred.status == "ACTIVE"

    # 2. Citizen presents credential
    pres_req = DigiInRequest.create(
        actor_type="USER",
        actor_id=auth.user_id,
        action=UserActionTypes.PRESENT_CREDENTIAL,
        payload={"credentialId": cred.id, "verifierId": "ver_corp"}
    )
    pres_res = cred_workflow.handle_present_credential(pres_req, auth)
    assert pres_res.success is True
    assert pres_res.data["status"] == "VALID"

    # 3. University Revokes Credential
    assert cred_workflow.revoke_credential(cred.id, "STUDENT_EXPELLED") is True

    # 4. Presentation of revoked credential is now rejected
    pres_res_rev = cred_workflow.handle_present_credential(pres_req, auth)
    assert pres_res_rev.success is False
    assert pres_res_rev.error["code"] == "CREDENTIAL_INVALID"
    print("    [PASS] Flow 3: Credential issuance, presentation and instant revocation verified")

def test_user_friendly_error_shielding():
    print(">>> 5. Testing User-Friendly Error Shielding...")
    # 1. Structured DigiInError
    err1 = DigiInError(
        code="CONSENT_REQUIRED",
        status_code=403,
        user_message="Your permission is required before this information can be shared."
    )
    safe_dict1 = ErrorSanitizer.sanitize_exception(err1, "req_err_01")
    assert safe_dict1["success"] is False
    assert safe_dict1["error"]["code"] == "CONSENT_REQUIRED"
    assert "permission is required" in safe_dict1["error"]["message"]

    # 2. Raw Exception (e.g. database crash / SQL error)
    err2 = RuntimeError("SQLSTATE[HY000]: General error: 2006 MySQL server has gone away")
    safe_dict2 = ErrorSanitizer.sanitize_exception(err2, "req_err_02")
    assert safe_dict2["success"] is False
    assert safe_dict2["error"]["code"] == "INTERNAL_SERVICE_ERROR"
    assert "MySQL" not in safe_dict2["error"]["message"]
    print("    [PASS] User-friendly error shielding and internal detail masking verified")

def run_all_working_product_tests():
    print("=" * 80)
    print("DIGIIN PHASE 31 WORKING PRODUCT & USER REQUEST HANDLING TEST MATRIX")
    print("=" * 80)
    test_request_envelope_and_idempotency()
    test_flow1_document_upload_and_verification()
    test_flow2_institutional_request_and_consent()
    test_flow3_credential_presentation_and_revocation()
    test_user_friendly_error_shielding()
    print("=" * 80)
    print("SUCCESS: ALL 5 WORKING PRODUCT & USER REQUEST HANDLING TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_working_product_tests()
