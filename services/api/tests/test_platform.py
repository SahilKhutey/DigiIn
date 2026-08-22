from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_student_vertical_slice_generates_trusted_proof() -> None:
    demo = client.post("/api/v1/platform/demo/student").json()

    assert demo["document"]["status"] == "VERIFIED"
    assert demo["verificationCase"]["status"] == "VERIFIED"
    assert demo["transaction"]["state"] == "COMPLETED"
    assert demo["proofResult"]["status"] == "VERIFIED"
    assert demo["proofResult"]["receipt"]["documentShared"] is False

    check = client.post(
        "/api/v1/verification/introspect",
        json={
            "token": demo["proofResult"]["proof"]["token"],
            "audience": demo["proofResult"]["audience"],
        },
    ).json()

    assert check["status"] == "TRUSTED_PROOF"


def test_proof_token_rejects_wrong_audience() -> None:
    demo = client.post("/api/v1/platform/demo/student").json()

    check = client.post(
        "/api/v1/verification/introspect",
        json={"token": demo["proofResult"]["proof"]["token"], "audience": "WRONG_PORTAL"},
    ).json()

    assert check["status"] == "AUDIENCE_MISMATCH"


def test_correction_request_and_approval_creates_version_2() -> None:
    # 1. Upload & classify document
    upload = client.post(
        "/api/v1/documents/upload",
        json={
            "filename": "marksheet-demo.pdf",
            "documentType": "CLASS_XII",
            "source": "CITIZEN_UPLOAD",
        },
    ).json()
    doc_id = upload["documentId"]
    assert upload["currentVersion"] == 1

    classified = client.post(f"/api/v1/documents/{doc_id}/classify").json()
    assert classified["status"] == "CLASSIFIED"

    # 2. File a correction request
    corr_payload = {
        "field": "student_name",
        "currentValue": "SAHIL KHTEY",
        "proposedValue": "SAHIL KHUTEY",
        "reason": "Name spelling error in official registry transcription",
        "evidenceDescription": "Aadhaar eKYC Name Transcript & Secondary School Certificate",
        "evidenceReference": "EVID-CBSE-2026-CORR",
    }
    corr_res = client.post(f"/api/v1/documents/{doc_id}/corrections", json=corr_payload)
    assert corr_res.status_code == 200
    corr = corr_res.json()
    assert corr["status"] == "PENDING_REVIEW"
    assert corr["documentId"] == doc_id
    corr_id = corr["requestId"]

    # 3. List corrections
    doc_corrs = client.get(f"/api/v1/documents/{doc_id}/corrections").json()
    assert any(c["requestId"] == corr_id for c in doc_corrs)

    all_corrs = client.get("/api/v1/corrections").json()
    assert any(c["requestId"] == corr_id for c in all_corrs)

    # 4. Officer approves the correction
    decision_payload = {
        "decision": "APPROVE",
        "reviewerId": "officer_cbse_exam_board",
        "note": "Spelling error confirmed against primary board gazette.",
    }
    decided = client.post(f"/api/v1/corrections/{corr_id}/decision", json=decision_payload).json()
    assert decided["status"] == "APPROVED"
    assert decided["resultingVersion"] == 2
    assert decided["reviewerId"] == "officer_cbse_exam_board"

    # 5. Verify document updated to v2 with corrected field
    versions = client.get(f"/api/v1/documents/{doc_id}/versions").json()
    assert len(versions) == 2

    v1 = next(v for v in versions if v["versionNumber"] == 1)
    v2 = next(v for v in versions if v["versionNumber"] == 2)

    assert v1["status"] == "SUPERSEDED"
    assert v1["supersededAt"] is not None

    assert v2["status"] == "ACTIVE"
    assert v2["parentVersionId"] == v1["versionId"]
    assert v2["metadata"]["student_name"] == "SAHIL KHUTEY"
    assert v2["authority"] == "officer_cbse_exam_board"

    # 6. Verify platform snapshot reflects changes
    snapshot = client.get("/api/v1/platform/snapshot").json()
    assert any(c["requestId"] == corr_id for c in snapshot["corrections"])
    assert any(v["versionId"] == v2["versionId"] for v in snapshot["versions"])


def test_correction_rejection_does_not_bump_version() -> None:
    upload = client.post(
        "/api/v1/documents/upload",
        json={
            "filename": "graduation-degree.pdf",
            "documentType": "GRADUATION",
            "source": "CITIZEN_UPLOAD",
        },
    ).json()
    doc_id = upload["documentId"]

    corr_payload = {
        "field": "cgpa",
        "currentValue": "7.5",
        "proposedValue": "9.8",
        "reason": "Requesting grade increase",
    }
    corr = client.post(f"/api/v1/documents/{doc_id}/corrections", json=corr_payload).json()
    corr_id = corr["requestId"]

    decided = client.post(
        f"/api/v1/corrections/{corr_id}/decision",
        json={
            "decision": "REJECT",
            "reviewerId": "officer_univ_evaluator",
            "note": "Score discrepancy not supported by university records.",
        },
    ).json()

    assert decided["status"] == "REJECTED"
    assert decided["resultingVersion"] is None

    versions = client.get(f"/api/v1/documents/{doc_id}/versions").json()
    assert len(versions) == 1
    assert versions[0]["status"] == "ACTIVE"
    assert versions[0]["versionNumber"] == 1


def test_wallet_documents_return_5_discrete_trust_signals() -> None:
    wallet = client.get("/api/v1/wallet/documents").json()
    assert len(wallet) >= 4

    # 1. Check Class XII (Government Issued, Verified, Active, Level 4)
    cbse = next((d for d in wallet if d["documentId"] == "doc_cbse_xii_2026"), None)
    assert cbse is not None
    assert cbse["source"] == "GOVERNMENT_ISSUED"
    assert cbse["authenticity"] == "VERIFIED"
    assert cbse["validityStatus"] == "ACTIVE"
    assert cbse["verificationLevel"] == 4
    assert cbse["currentVersion"] == 1

    # 2. Check Driving Licence (Government Issued, Verified, EXPIRED, Level 5)
    dl = next((d for d in wallet if d["documentId"] == "doc_dl_morth_9811"), None)
    assert dl is not None
    assert dl["source"] == "GOVERNMENT_ISSUED"
    assert dl["authenticity"] == "VERIFIED"
    assert dl["validityStatus"] == "EXPIRED"
    assert dl["verificationLevel"] == 5

    # 3. Check Citizen Upload (Citizen Upload, UNKNOWN Authenticity, Active, Level 0)
    upload = next((d for d in wallet if d["documentId"] == "doc_upload_skill_7731"), None)
    assert upload is not None
    assert upload["authenticity"] == "UNKNOWN"
    assert upload["verificationLevel"] == 0

    # 4. Check Legacy Record (Legacy Record, Verified, Active, Level 4)
    legacy = next((d for d in wallet if d["documentId"] == "doc_land_revenue_1998"), None)
    assert legacy is not None
    assert legacy["authenticity"] == "VERIFIED"
    assert legacy["verificationLevel"] == 4


def test_verifier_queues_and_cases_listing() -> None:
    # 1. Fetch queues summary
    queues = client.get("/api/v1/verifier/queues").json()
    assert len(queues) == 4
    queue_ids = [q["queueId"] for q in queues]
    assert "queue_cbse" in queue_ids
    assert "queue_revenue" in queue_ids
    assert "queue_transport" in queue_ids
    assert "queue_general" in queue_ids

    # 2. Fetch cases for CBSE queue
    cbse_cases = client.get("/api/v1/verifier/cases?queue_id=queue_cbse").json()
    assert len(cbse_cases) >= 1
    assert any(c["caseId"] == "case_cbse_001" for c in cbse_cases)


def test_verifier_evidence_comparison_diff() -> None:
    diff = client.get("/api/v1/verifier/cases/case_cbse_001/comparison").json()
    assert diff["caseId"] == "case_cbse_001"
    assert diff["documentType"] == "CLASS_XII"
    assert diff["overallMatchScore"] == 94
    assert len(diff["fieldComparisons"]) >= 4

    name_match = next((f for f in diff["fieldComparisons"] if f["field"] == "student_name"), None)
    assert name_match is not None
    assert name_match["citizenValue"] == "SAHIL KHUTEY"
    assert name_match["registryValue"] == "SAHIL KHUTEY"
    assert name_match["isMatch"] is True


def test_verifier_officer_decision_and_queue_transfer() -> None:
    # 1. Transfer case_transport_001 to queue_revenue
    transfer_payload = {
        "decision": "TRANSFER",
        "verifierId": "officer_transport_superintendent",
        "note": "Citizen has attached a land record as additional domicile proof. Routing to Revenue department queue.",
        "transferQueue": "queue_revenue",
    }
    transferred = client.post("/api/v1/verifier/cases/case_transport_001/decision", json=transfer_payload).json()
    assert transferred["verifierQueue"] == "queue_revenue"
    assert transferred["status"] == "UNDER_REVIEW"

    # 2. Verify case_skill_001 and promote to Level 4
    verify_payload = {
        "decision": "VERIFY",
        "verifierId": "officer_state_evaluator_04",
        "note": "Verified with training council registry.",
    }
    verified = client.post("/api/v1/verifier/cases/case_skill_001/decision", json=verify_payload).json()
    assert verified["status"] == "VERIFIED"

    # Check that the underlying document was updated to Level 4 VERIFIED
    snapshot = client.get("/api/v1/platform/snapshot").json()
    doc = next((d for d in snapshot["documents"] if d["documentId"] == "doc_upload_skill_7731"), None)
    assert doc is not None
    assert doc["status"] == "VERIFIED"
    assert doc["verificationLevel"] == 4


def test_document_upload_and_ocr_classification_pipeline() -> None:
    payload = {
        "ownerSubjectId": "subj_demo_5c7b90",
        "filename": "state_land_title_deed_1998_scan.pdf",
        "documentTypeHint": "LAND_RECORD",
        "simulatedContent": "DEED_1998_DISTRICT_RAIPUR_SURVEY_98_104_SAHIL_KHUTEY",
    }
    res = client.post("/api/v1/documents/upload-pipeline", json=payload)
    assert res.status_code == 200
    data = res.json()

    # 1. Check Document properties
    doc = data["document"]
    assert doc["documentType"] == "LAND_RECORD"
    assert doc["verificationLevel"] == 2
    assert doc["status"] == "PENDING_VERIFICATION"

    # 2. Check OCR classification
    clf = data["classification"]
    assert clf["documentType"] == "LAND_RECORD"
    assert clf["confidenceScore"] == 88
    assert clf["suggestedQueue"] == "queue_revenue"
    assert len(clf["sha256"]) == 64
    assert clf["extractedFields"]["survey_number"] == "SUR-98/104"

    # 3. Check Verification Case creation
    case = data["verificationCase"]
    assert case["verifierQueue"] == "queue_revenue"
    assert case["status"] == "UNDER_REVIEW"

    # 4. Check WalletDocument response
    wallet_doc = data["walletDocument"]
    assert wallet_doc["source"] == "CITIZEN_UPLOAD"
    assert wallet_doc["authenticity"] == "UNKNOWN"
    assert wallet_doc["verificationLevel"] == 2


def test_support_safe_summary_generation() -> None:
    # 1. Identity mismatch scenario
    summary = client.get("/api/v1/transactions/identity-mismatch/support-summary").json()
    assert summary["scenarioId"] == "identity-mismatch"
    assert summary["supportCode"].startswith("DIGIIN-REC-")
    assert summary["failureStage"] == "IDENTITY_MATCH_MISMATCH"
    assert "CBSE" in summary["affectedAuthority"]
    assert len(summary["guidanceForCitizen"]) >= 2
    assert len(summary["guidanceForDeskOfficer"]) >= 2
    assert "password" not in summary["plainLanguageExplanation"].lower()

    # 2. Issuer unavailable scenario
    summary_iu = client.get("/api/v1/transactions/issuer-unavailable/support-summary").json()
    assert summary_iu["failureStage"] == "ISSUER_GATEWAY_TIMEOUT"
    assert "DEGRADED" in summary_iu["issuerStatus"]


def test_jwks_discovery_endpoint() -> None:
    res1 = client.get("/.well-known/jwks.json")
    assert res1.status_code == 200
    jwks1 = res1.json()
    assert "keys" in jwks1
    assert len(jwks1["keys"]) == 2

    # Check Ed25519 key
    ed_key = next((k for k in jwks1["keys"] if k["kty"] == "OKP"), None)
    assert ed_key is not None
    assert ed_key["alg"] == "EdDSA"
    assert ed_key["crv"] == "Ed25519"
    assert "x" in ed_key
    assert ed_key["kid"] == "digiin-ed25519-key-2026"

    # Check RSA key
    rsa_key = next((k for k in jwks1["keys"] if k["kty"] == "RSA"), None)
    assert rsa_key is not None
    assert rsa_key["alg"] == "RS256"
    assert "n" in rsa_key and "e" in rsa_key
    assert rsa_key["kid"] == "digiin-rs256-key-2026"

    # Check alias route
    res2 = client.get("/api/v1/.well-known/jwks.json")
    assert res2.status_code == 200
    assert len(res2.json()["keys"]) == 2


def test_asymmetric_eddsa_and_rs256_cryptographic_verification() -> None:
    from app.services.crypto import sign_proof_token, verify_proof_token

    # 1. Test Ed25519 Token Signing & Offline Verification
    claims = {
        "iss": "DigiIn Synthetic Verification Gateway",
        "sub": "subj_demo_5c7b90",
        "aud": "DELHI_UNIVERSITY_ADMISSION",
        "purpose": "ADMISSION_VERIFICATION",
        "verification_id": "ver_crypto_test_01",
        "status": "VERIFIED",
        "iat": "2026-08-22T12:00:00Z",
        "exp": "2026-08-22T13:00:00Z",
    }
    ed_token, ed_kid, ed_alg = sign_proof_token(claims, algorithm="EdDSA")
    assert ed_alg == "EdDSA"
    assert ed_kid == "digiin-ed25519-key-2026"

    verified_claims, verified_kid, verified_alg = verify_proof_token(ed_token)
    assert verified_claims is not None
    assert verified_claims["verification_id"] == "ver_crypto_test_01"
    assert verified_kid == ed_kid
    assert verified_alg == "EdDSA"

    # 2. Test RS256 Token Signing & Offline Verification
    rsa_token, rsa_kid, rsa_alg = sign_proof_token(claims, algorithm="RS256")
    assert rsa_alg == "RS256"
    assert rsa_kid == "digiin-rs256-key-2026"

    rsa_verified, rsa_v_kid, rsa_v_alg = verify_proof_token(rsa_token)
    assert rsa_verified is not None
    assert rsa_verified["verification_id"] == "ver_crypto_test_01"
    assert rsa_v_kid == rsa_kid
    assert rsa_v_alg == "RS256"

    # 3. Test Tampered Token Rejection
    header_part, claims_part, sig_part = ed_token.split(".")
    tampered_claims = claims_part[:-4] + "AAAA"
    tampered_token = f"{header_part}.{tampered_claims}.{sig_part}"
    bad_claims, _, _ = verify_proof_token(tampered_token)
    assert bad_claims is None

    # 4. Test Introspection Endpoint with Asymmetric Token
    intro_res = client.post(
        "/api/v1/verification/introspect",
        json={"token": ed_token, "audience": "DELHI_UNIVERSITY_ADMISSION"},
    )
    assert intro_res.status_code == 200
    intro_data = intro_res.json()
    assert intro_data["active"] is True
    assert intro_data["status"] == "TRUSTED_PROOF"
    assert intro_data["algorithm"] == "EdDSA"
    assert intro_data["keyId"] == "digiin-ed25519-key-2026"
    assert intro_data["cryptoVerified"] is True


def test_database_health_endpoint() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["mode"] == "persistent-relational"
    assert data["database"]["status"] == "connected"
    assert data["database"]["dialect"] == "sqlite"


def test_database_persistence_and_repository_crud() -> None:
    from datetime import UTC, datetime
    from app.db import repository as repo
    from app.domain.models import DocumentVersionStatus, UploadedDocument, DocumentVersionRecord

    now = datetime.now(UTC)

    test_doc = UploadedDocument(
        documentId="doc_test_db_persist_01",
        ownerSubjectId="subj_demo_5c7b90",
        documentType="CLASS_XII",
        source="CITIZEN_UPLOAD",
        filename="marksheet_db_test.pdf",
        status="PENDING_VERIFICATION",
        authenticity="UNKNOWN",
        verificationLevel=2,
        currentVersion=1,
        extractedMetadata={"student_name": "Sahil Khutey", "test_key": "db_val_100"},
        createdAt=now,
    )
    repo.save_document(test_doc)

    # 1. Fetch document from relational table
    fetched = repo.get_document("doc_test_db_persist_01")
    assert fetched is not None
    assert fetched.documentId == "doc_test_db_persist_01"
    assert fetched.extractedMetadata["test_key"] == "db_val_100"

    # 2. Add version record to relational table
    v1 = DocumentVersionRecord(
        versionId="ver_test_db_v1",
        versionNumber=1,
        documentId="doc_test_db_persist_01",
        status=DocumentVersionStatus.ACTIVE,
        metadata={"test_key": "db_val_100"},
        changeSummary="Initial DB persistence test.",
        authority="CBSE Authority",
        createdAt=now,
    )
    repo.save_document_version(v1)

    versions = repo.get_document_versions("doc_test_db_persist_01")
    assert len(versions) >= 1
    assert versions[0].versionId == "ver_test_db_v1"

    # 3. Check wallet documents query from relational DB
    wallet_docs = repo.list_wallet_documents("subj_demo_5c7b90")
    assert len(wallet_docs) >= 1


def test_zero_knowledge_predicate_mode_evaluation() -> None:
    from app.domain.models import SelectiveDisclosurePreference, VerificationAuthorization
    from app.services.verification import (
        authorize_verification_request,
        create_verification_request,
        demo_exam_request,
    )

    # 1. Create standard exam request
    req = create_verification_request(demo_exam_request())

    # 2. Authorize in Zero-Knowledge Predicate Mode
    auth = VerificationAuthorization(
        allow=True,
        subjectId="subj_demo_5c7b90",
        customDisclosure=SelectiveDisclosurePreference(
            mode="PREDICATE_ONLY",
            selectedAttributes=[],
            selectedPredicates=["AGE_OVER_18", "CLASS_XII", "DOMICILE"],
        ),
    )
    result = authorize_verification_request(req.requestId, auth)
    assert result is not None
    assert result.status == "VERIFIED"
    assert result.disclosureLevel == "BOOLEAN"

    # 3. Check derived predicate proofs
    assert len(result.predicateProofs) >= 3
    for p in result.predicateProofs:
        assert p.satisfied is True
        assert p.proofType == "DERIVED_ZERO_KNOWLEDGE_PREDICATE"

    # 4. Verify raw attributes are empty and sensitive fields are masked
    for cred_res in result.results:
        assert cred_res.disclosedAttributes == {}
        assert len(cred_res.maskedAttributes) > 0

    assert any("roll_number" in m or "date_of_birth" in m for m in result.maskedAttributesSummary)


def test_selective_attribute_custom_mode_evaluation() -> None:
    from app.domain.models import SelectiveDisclosurePreference, VerificationAuthorization
    from app.services.verification import (
        authorize_verification_request,
        create_verification_request,
        demo_exam_request,
    )


    req = create_verification_request(demo_exam_request())

    # Authorize with selective custom fields: only 'qualification'
    auth = VerificationAuthorization(
        allow=True,
        subjectId="subj_demo_5c7b90",
        customDisclosure=SelectiveDisclosurePreference(
            mode="SELECTIVE_ATTRIBUTES",
            selectedAttributes=["qualification"],
            selectedPredicates=[],
        ),
    )
    result = authorize_verification_request(req.requestId, auth)
    assert result is not None
    assert result.status == "VERIFIED"
    assert result.disclosureLevel == "ATTRIBUTE"

    class12_res = next(r for r in result.results if r.credential == "CLASS_XII")
    assert "qualification" in class12_res.disclosedAttributes
    assert "roll_number" not in class12_res.disclosedAttributes
    assert "roll_number" in class12_res.maskedAttributes


def test_consent_listing_and_token_revocation() -> None:
    from app.services.verification import (
        authorize_verification_request,
        create_verification_request,
        demo_exam_request,
        introspect_token,
    )
    from app.domain.models import VerificationAuthorization

    # 1. Authorize a verification request
    req = create_verification_request(demo_exam_request())
    auth = VerificationAuthorization(allow=True, subjectId="subj_demo_5c7b90")
    result = authorize_verification_request(req.requestId, auth)
    assert result is not None
    v_id = result.verificationId

    # 2. Check that it appears in GET /api/v1/consent
    consent_res = client.get("/api/v1/consent?subject_id=subj_demo_5c7b90")
    assert consent_res.status_code == 200
    consents = consent_res.json()
    assert len(consents) >= 1
    c_match = next((c for c in consents if c["verificationId"] == v_id), None)
    assert c_match is not None
    assert c_match["status"] == "ACTIVE"
    assert c_match["requesterName"] == "Demo Examination Portal"

    # 3. Verify token is active before revocation
    intro_before = introspect_token(result.proof.token, result.audience)
    assert intro_before.active is True
    assert intro_before.status == "TRUSTED_PROOF"

    # 4. Revoke consent via POST /api/v1/consent/{id}/revoke
    revoke_res = client.post(
        f"/api/v1/consent/{v_id}/revoke",
        json={"reason": "Citizen decided to cancel exam application."},
    )
    assert revoke_res.status_code == 200
    revoked_consent = revoke_res.json()
    assert revoked_consent["status"] == "REVOKED"
    assert revoked_consent["revocationReason"] == "Citizen decided to cancel exam application."

    # 5. Verify introspection now reports REVOKED
    intro_after = introspect_token(result.proof.token, result.audience)
    assert intro_after.active is False
    assert intro_after.status == "REVOKED"
    assert "revoked by the citizen" in intro_after.message


def test_ekyc_otp_generation_verification_and_demographic_matching() -> None:
    # 1. Generate eKYC OTP for valid Virtual ID
    otp_req = {"aadhaarRef": "9100-2026-9921", "purpose": "Exam Application Identity Verification"}
    otp_res = client.post("/api/v1/ekyc/generate-otp", json=otp_req)
    assert otp_res.status_code == 200
    otp_data = otp_res.json()
    assert "txnId" in otp_data
    assert otp_data["demoOtpHint"] == "202601"
    assert otp_data["maskedMobile"] == "+91 ******9921"
    txn_id = otp_data["txnId"]

    # 2. Test Invalid OTP rejection (Security boundary)
    bad_verify = client.post(
        "/api/v1/ekyc/verify-otp",
        json={"txnId": txn_id, "otp": "000000"},
    )
    assert bad_verify.status_code == 400
    assert "Invalid OTP entered" in bad_verify.json()["detail"]

    # 3. Test Valid OTP verification & Demographic matching
    good_verify = client.post(
        "/api/v1/ekyc/verify-otp",
        json={"txnId": txn_id, "otp": "202601", "documentId": "doc_cbse_xii_2026"},
    )
    assert good_verify.status_code == 200
    verify_data = good_verify.json()
    assert verify_data["status"] == "VERIFIED"
    assert verify_data["identitySnapshot"]["name"] == "SAHIL KHUTEY"
    assert verify_data["identitySnapshot"]["maskedAadhaar"] == "XXXXXXXX9921"
    assert verify_data["matchResult"]["nameMatch"] is True
    assert verify_data["matchResult"]["score"] >= 90
    assert verify_data["elevatedDocumentLevel"] == 4
    assert "ekycProofToken" in verify_data
    assert verify_data["algorithm"] == "EdDSA"

    # 4. Test Standalone Demographics Match Endpoint (Fuzzy Match)
    fuzzy_match_res = client.post(
        "/api/v1/ekyc/match-demographics",
        json={
            "aadhaarRef": "9100-2026-9921",
            "claimedName": "SAHIL KHTEY",  # 1-char spelling discrepancy
            "claimedDob": "2006-05-14",
            "claimedState": "Chhattisgarh",
        },
    )
    assert fuzzy_match_res.status_code == 200
    fuzzy_data = fuzzy_match_res.json()
    assert fuzzy_data["nameMatch"] is True
    assert fuzzy_data["dobMatch"] is True
    assert fuzzy_data["score"] >= 85











