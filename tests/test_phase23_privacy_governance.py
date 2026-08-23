"""
DigiIn Automated Privacy, Data Governance & Compliance Test Suite (Phase 23)
Validates Data Classification, Purpose Limitation, Consent Engine, Minimization, Retention & Legal Holds, Data Export, Account Closure, and Privacy Auditing.
"""

import sys
import os
import time

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.privacy_governance import (
    DataClassification,
    DataAssetRegistry,
    DataPurposeRegistry,
    ConsentPolicyEngine,
    DataMinimizer,
    RetentionScheduler,
    DataExportService,
    AccountClosureManager,
    PrivacyAuditLogger,
    ProviderDataGovernance,
    ComplianceRegistry,
    PrivacyIncidentManager,
)

def test_data_classification_and_purpose_registry():
    print(">>> 1. Testing Data Classification & Purpose Limitation...")
    asset_reg = DataAssetRegistry()
    purpose_reg = DataPurposeRegistry()

    # 1. Asset Registry lookup
    doc_asset = asset_reg.get_asset("asset_uploaded_document")
    assert doc_asset is not None
    assert doc_asset.classification == DataClassification.SENSITIVE_PERSONAL
    assert doc_asset.owner == "Citizen"

    # 2. Purpose Limitation: Education verification allows PUBLIC & PERSONAL data classes
    assert purpose_reg.is_data_class_allowed_for_purpose("EDUCATION_VERIFICATION", DataClassification.PERSONAL) is True
    # Education verification does NOT allow CRYPTOGRAPHIC_SECRET data class
    assert purpose_reg.is_data_class_allowed_for_purpose("EDUCATION_VERIFICATION", DataClassification.CRYPTOGRAPHIC_SECRET) is False
    print("    [PASS] Data classification & purpose limitation boundaries verified")

def test_consent_engine_and_revocation():
    print(">>> 2. Testing Consent Binding & Instant Revocation...")
    consent_engine = ConsentPolicyEngine()

    # 1. Grant consent for Education Verification
    consent = consent_engine.grant_consent(
        subject_id="subj_rahul_99",
        purpose_code="EDUCATION_VERIFICATION",
        scope=["education:degree", "education:marksheet"],
        recipient_id="app_delhi_university",
        ttl_seconds=3600
    )
    assert consent.status == "ACTIVE"

    # 2. Evaluate authorized access -> ALLOW
    ok, err, rec = consent_engine.evaluate_access(
        subject_id="subj_rahul_99",
        recipient_id="app_delhi_university",
        purpose_code="EDUCATION_VERIFICATION",
        requested_scope="education:degree"
    )
    assert ok is True

    # 3. Request un-granted scope -> DENY (SCOPE_UNAUTHORIZED)
    ok_unauth, err_unauth, _ = consent_engine.evaluate_access(
        subject_id="subj_rahul_99",
        recipient_id="app_delhi_university",
        purpose_code="EDUCATION_VERIFICATION",
        requested_scope="financial:bank_account"
    )
    assert ok_unauth is False
    assert "SCOPE_UNAUTHORIZED" in err_unauth

    # 4. Revoke consent -> Immediate DENY (CONSENT_EXPLICITLY_REVOKED)
    assert consent_engine.revoke_consent(consent.id) is True
    ok_revoked, err_revoked, _ = consent_engine.evaluate_access(
        subject_id="subj_rahul_99",
        recipient_id="app_delhi_university",
        purpose_code="EDUCATION_VERIFICATION",
        requested_scope="education:degree"
    )
    assert ok_revoked is False
    assert err_revoked == "CONSENT_EXPLICITLY_REVOKED"
    print("    [PASS] Consent policy evaluation & instant revocation verified")

def test_data_minimization_and_provider_governance():
    print(">>> 3. Testing Data Minimization & Provider Governance...")
    full_evidence = {
        "status": "VERIFIED",
        "verifiedAt": 1771800000,
        "degree": "Bachelor of Technology in Computer Science",
        "institution": "Indian Institute of Technology",
        "dob": "1998-05-14",
        "aadhaar": "9988-7766-5544",
        "rawDocumentBytes": b"%PDF-1.4...",
        "internalDbId": 994821
    }

    # Minimize evidence payload
    minimized = DataMinimizer.minimize_verification_result(
        full_evidence=full_evidence,
        authorized_scopes=["education:degree", "identity:age_over_18"]
    )

    assert minimized["verificationStatus"] == "VERIFIED"
    assert minimized["minimalClaims"]["degree"] == "Bachelor of Technology in Computer Science"
    assert minimized["minimalClaims"]["isOver18"] is True
    assert "aadhaar" not in minimized["minimalClaims"]
    assert "rawDocumentBytes" not in minimized
    assert minimized["rawDocumentExcluded"] is True

    # Provider egress sanitization
    egress = ProviderDataGovernance.sanitize_provider_egress("subj_01", "DEGREE_CERTIFICATE", "cbse-01")
    assert egress["subjectReference"] == "subj_01"
    assert egress["crossAccountLinkageExcluded"] is True
    print("    [PASS] Attribute-level data minimization & provider governance verified")

def test_retention_engine_and_legal_holds():
    print(">>> 4. Testing Retention Engine & Legal Hold Locks...")
    retention = RetentionScheduler()

    # 1. Old record without legal hold -> DELETE
    now = time.time()
    created_old = now - (86400 * 35)  # 35 days ago (policy is 30d)
    should_delete, reason = retention.evaluate_record_for_deletion(
        resource_type="DOCUMENT",
        resource_id="doc_expired_01",
        created_at=created_old,
        policy_id="RET_DOC_VERIFICATION_30D"
    )
    assert should_delete is True
    assert "RETENTION_EXPIRED" in reason

    # 2. Place Legal Hold -> PAUSE deletion
    hold = retention.place_legal_hold("DOCUMENT", "doc_expired_01", "Ongoing statutory inquiry", created_by="Officer_Sharma")
    assert hold.active is True

    should_delete_held, reason_held = retention.evaluate_record_for_deletion(
        resource_type="DOCUMENT",
        resource_id="doc_expired_01",
        created_at=created_old,
        policy_id="RET_DOC_VERIFICATION_30D"
    )
    assert should_delete_held is False
    assert "LEGAL_HOLD_ACTIVE" in reason_held

    # 3. Release Legal Hold -> Resume deletion eligibility
    assert retention.release_legal_hold(hold.id) is True
    should_delete_released, _ = retention.evaluate_record_for_deletion(
        resource_type="DOCUMENT",
        resource_id="doc_expired_01",
        created_at=created_old,
        policy_id="RET_DOC_VERIFICATION_30D"
    )
    assert should_delete_released is True
    print("    [PASS] Retention scheduler & legal hold locks verified")

def test_data_export_and_account_closure():
    print(">>> 5. Testing Citizen Data Export & Account Closure...")
    export_svc = DataExportService()
    closure_mgr = AccountClosureManager()

    # 1. Citizen Data Export package
    exp = export_svc.generate_export_package(
        citizen_id="citizen_rahul_99",
        profile_data={"name": "Rahul Sharma", "tier": "SOVEREIGN"},
        verifications=[{"id": "ver_01", "type": "DEGREE", "status": "VERIFIED"}],
        consents=[{"id": "cst_01", "purpose": "EDUCATION_VERIFICATION"}],
        proofs=[{"id": "prf_01", "keyId": "KEY-2026"}]
    )
    assert exp["exportId"] is not None
    assert "token=" in exp["downloadUrl"]
    assert exp["package"]["compliance"] == "DPDP_ACT_2023_PORTABILITY_COMPLIANT"

    # 2. Account Closure Pipeline with MFA & Dependency validation
    req = closure_mgr.initiate_closure("citizen_rahul_99")
    assert req.state == "REQUESTED"

    # Blocked if active legal hold present
    ok_blocked, msg_blocked, _ = closure_mgr.process_closure_pipeline(
        closure_id=req.id,
        is_reauthenticated=True,
        has_active_legal_hold=True
    )
    assert ok_blocked is False
    assert "CLOSURE_BLOCKED" in msg_blocked

    # Clean closure -> SUCCESS
    ok_closed, msg_closed, closed_rec = closure_mgr.process_closure_pipeline(
        closure_id=req.id,
        is_reauthenticated=True,
        has_active_legal_hold=False
    )
    assert ok_closed is True
    assert closed_rec.state == "CLOSED"
    assert closed_rec.closed_at is not None
    print("    [PASS] Citizen data export & 6-stage account closure verified")

def test_privacy_audit_and_incident_containment():
    print(">>> 6. Testing Privacy Auditing & Incident Containment...")
    audit_logger = PrivacyAuditLogger()
    inc_mgr = PrivacyIncidentManager()
    comp_reg = ComplianceRegistry()

    # 1. Privacy Audit Logging (Allowed & Denied)
    audit_logger.log_access(
        actor_id="app_delhi_university",
        actor_type="API_CLIENT",
        action="VERIFY",
        resource_type="VERIFICATION_CLAIM",
        resource_id="vcl_0182",
        purpose_code="EDUCATION_VERIFICATION",
        outcome="ALLOWED"
    )

    audit_logger.log_access(
        actor_id="app_rogue_service",
        actor_type="API_CLIENT",
        action="READ",
        resource_type="DOCUMENT_RAW",
        resource_id="doc_8899",
        purpose_code="UNREGISTERED_PURPOSE",
        outcome="DENIED",
        reason="Purpose not registered in data governance catalogue"
    )

    assert len(audit_logger.list_events_for_resource("vcl_0182")) == 1
    assert len(audit_logger.list_denied_events()) == 1

    # 2. Privacy Incident Containment
    inc = inc_mgr.report_incident("Suspected Token Leakage on Partner API", severity="HIGH", affected_count=1)
    assert inc.stage == "DETECTED"

    _, inc_contained = inc_mgr.execute_containment(inc.id, "REVOKE_OAUTH_CLIENT_CREDENTIALS")
    assert inc_contained.stage == "CONTAINED"
    assert "REVOKE_OAUTH_CLIENT_CREDENTIALS" in inc_contained.containment_actions

    # 3. Compliance Control Posture
    posture = comp_reg.get_compliance_posture()
    assert posture["implemented"] >= 4
    assert "DPDP Act 2023" in posture["frameworks"]
    print("    [PASS] Privacy auditing, incident containment & compliance posture verified")

def run_all_privacy_governance_tests():
    print("=" * 80)
    print("DIGIIN PHASE 23 PRIVACY, DATA GOVERNANCE & COMPLIANCE TEST MATRIX")
    print("=" * 80)
    test_data_classification_and_purpose_registry()
    test_consent_engine_and_revocation()
    test_data_minimization_and_provider_governance()
    test_retention_engine_and_legal_holds()
    test_data_export_and_account_closure()
    test_privacy_audit_and_incident_containment()
    print("=" * 80)
    print("SUCCESS: ALL 6 PRIVACY, DATA GOVERNANCE & COMPLIANCE TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_privacy_governance_tests()
