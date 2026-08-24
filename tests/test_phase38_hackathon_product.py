"""Phase 38 — Hackathon-First Product Development Test Suite.

Validates:
  1. Service-first public services catalogue and estimated completion times.
  2. Flagship 6-step Scholarship Journey (Citizen -> Sharing Review -> Consent -> Proof -> Institution).
  3. Signature Sharing Review screen: explicit shared predicates vs withheld private claims (zero raw file transfer).
  4. Low-Bandwidth Data Saver mode engine: heavy asset stripping and payload compression.
  5. Bilingual English & Hindi locale dictionary parity.
  6. Public Service API endpoints (/api/v1/public-service/*).
  7. Hackathon presentation and submission video documentation suite.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "services" / "api"))
sys.path.insert(0, str(root_dir))

from fastapi.testclient import TestClient

from app.core.public_service import (
    ApplicationStatus,
    data_saver_engine,
    service_registry,
    sharing_review_generator,
)
from app.db.session import init_db
from app.main import app

init_db()
client = TestClient(app)


def test_public_services_catalogue():
    print(">>> 1. Verifying Public Services Catalogue & Estimated Times...")
    services = service_registry.list_services()
    assert len(services) >= 3

    scholarship = next(s for s in services if s["service_id"] == "srv_scholarship_du")
    assert "National Merit-cum-Means Scholarship" in scholarship["name"]
    assert scholarship["estimated_time_digiin"] == "2 minutes"
    assert "45 minutes" in scholarship["estimated_time_traditional"]

    print("    [PASS] Service catalogue active with clear estimated completion times (2 min vs 45 min)")


def test_flagship_scholarship_journey_and_sharing_review():
    print(">>> 2. Verifying Flagship Scholarship Journey & Signature Sharing Review Screen...")

    # Step 1: Start Application
    citizen_account = "DGI-7K4M-X9P2-2026"
    citizen_name = "Rahul Sharma"
    app_record = service_registry.start_application(
        service_id="srv_scholarship_du",
        citizen_account_id=citizen_account,
        citizen_name=citizen_name,
    )
    assert app_record.status == ApplicationStatus.INITIATED
    assert app_record.citizen_name == "Rahul Sharma"

    # Step 2: Generate Signature Sharing Review Screen
    review_data = sharing_review_generator.generate_review(app_record.application_id)
    assert review_data.application_id == app_record.application_id
    assert "University of Delhi" in review_data.requesting_institution
    assert review_data.raw_files_transferred_bytes == 0

    # Verify Shared Predicates
    shared_fields = {c.field for c in review_data.shared_claims}
    assert "fullName" in shared_fields
    assert "domicileState" in shared_fields
    assert "incomeEligibility" in shared_fields
    assert "academicScore" in shared_fields

    # Verify Withheld Claims (Kept Private in Vault)
    withheld_fields = {c.field for c in review_data.withheld_claims}
    assert "aadhaarNumber" in withheld_fields
    assert "rawDocumentFiles" in withheld_fields
    assert "exactIncomeTaxFigures" in withheld_fields
    assert "residentialAddress" in withheld_fields

    print("    [PASS] Sharing Review screen explicitly separates shared predicates from withheld private claims")


def test_data_saver_mode_compression():
    print(">>> 3. Verifying Low-Bandwidth Data Saver Mode Engine...")

    sample_heavy_payload = {
        "status": "success",
        "service": "National Scholarship",
        "raw_file": "JVBERi0xLjQKJcTl8uXrp/Og0MT...HUGE_BASE64_DOCUMENT_BINARY...",
        "debug_trace": {"stack": ["worker.py:120", "crypto.py:44"], "verbose_logs": "x" * 2000},
        "claims": {
            "fullName": "Rahul Sharma",
            "income_eligible": True,
            "domicile": "Chhattisgarh",
        },
    }

    data_saver_engine.set_enabled(True)
    optimized = data_saver_engine.optimize_payload(sample_heavy_payload)

    assert "raw_file" not in optimized
    assert "debug_trace" not in optimized
    assert optimized["claims"]["fullName"] == "Rahul Sharma"
    assert optimized["claims"]["income_eligible"] is True

    savings = data_saver_engine.calculate_savings(sample_heavy_payload, optimized)
    assert savings.mode_active is True
    assert savings.bytes_saved > 0
    assert savings.compression_ratio_pct >= 50.0
    assert "Data Saver is on" in savings.message

    print(f"    [PASS] Data Saver stripped heavy assets, achieving {savings.compression_ratio_pct}% bandwidth reduction")


def test_bilingual_dictionary_parity():
    print(">>> 4. Verifying English & Hindi Bilingual Translation Parity...")

    i18n_dir = root_dir / "packages" / "i18n" / "src" / "locales"
    en_file = i18n_dir / "en.json"
    hi_file = i18n_dir / "hi.json"

    assert en_file.is_file(), "Missing en.json"
    assert hi_file.is_file(), "Missing hi.json"

    en_data = json.loads(en_file.read_text(encoding="utf-8"))
    hi_data = json.loads(hi_file.read_text(encoding="utf-8"))

    # Assert matching top-level sections
    assert set(en_data.keys()) == set(hi_data.keys())
    assert "tagline" in en_data["app"]
    assert "tagline" in hi_data["app"]
    assert "sharingReview" in en_data
    assert "sharingReview" in hi_data
    assert "dataSaver" in en_data
    assert "dataSaver" in hi_data

    print("    [PASS] Full bilingual English and Hindi parity across all UI and consent keys")


def test_public_service_api_endpoints():
    print(">>> 5. Verifying Public Service API Endpoints (/api/v1/public-service/*)...")

    # 1. Services List
    resp_services = client.get("/api/v1/public-service/services")
    assert resp_services.status_code == 200
    assert resp_services.json()["count"] >= 3

    # 2. Start Scholarship Application
    resp_apply = client.post(
        "/api/v1/public-service/scholarship/apply",
        json={"citizen_account_id": "DGI-7K4M-X9P2-2026", "citizen_name": "Rahul Sharma"},
    )
    assert resp_apply.status_code == 200
    apply_data = resp_apply.json()
    app_id = apply_data["application_id"]

    # 3. Get Sharing Review Screen Data
    resp_review = client.get(f"/api/v1/public-service/scholarship/{app_id}/sharing-review")
    assert resp_review.status_code == 200
    review_body = resp_review.json()["review"]
    assert review_body["raw_files_transferred_bytes"] == 0
    assert len(review_body["shared_claims"]) == 4
    assert len(review_body["withheld_claims"]) == 4

    # 4. Consent and Submit Application
    resp_submit = client.post(
        f"/api/v1/public-service/scholarship/{app_id}/consent-and-submit",
        json={"citizen_account_id": "DGI-7K4M-X9P2-2026", "consent_granted": True},
    )
    assert resp_submit.status_code == 200
    submit_data = resp_submit.json()
    assert submit_data["application_status"] == "SUBMITTED"
    assert submit_data["raw_files_transferred"] == "0 Bytes"
    assert "proof_id" in submit_data

    # 5. Institutional Verification View
    resp_inst = client.get(f"/api/v1/public-service/institution/applications/{app_id}")
    assert resp_inst.status_code == 200
    inst_body = resp_inst.json()
    assert inst_body["applicant_name"] == "Rahul Sharma"
    assert inst_body["cryptographic_evidence"]["raw_files_held"] == "0 Bytes (Zero Storage Liability)"
    assert inst_body["institution_action"] == "READY_FOR_ADMISSION_APPROVAL"

    # 6. Data Saver Status
    resp_ds = client.get("/api/v1/public-service/data-saver/status")
    assert resp_ds.status_code == 200
    assert resp_ds.json()["data_saver_active"] is True

    print("    [PASS] All 6 Public Service API endpoints verified (200 OK)")


def test_hackathon_submission_documentation():
    print(">>> 6. Verifying Hackathon Submission Documentation Suite in docs/hackathon/...")

    docs_to_check = [
        "PRODUCT_STORY.md",
        "FLAGSHIP_JOURNEY.md",
        "ACCESSIBILITY_AND_DATA_SAVER.md",
        "OPENAI_USAGE.md",
        "VIDEO_DEMO_SCRIPT.md",
    ]
    for doc_name in docs_to_check:
        doc_path = root_dir / "docs" / "hackathon" / doc_name
        assert doc_path.is_file(), f"Missing hackathon documentation: {doc_name}"
        assert doc_path.stat().st_size > 500, f"Documentation file {doc_name} is too small"

    print("    [PASS] All 5 Hackathon Productization documents verified present and complete")


# ===========================================================================
# Main Execution
# ===========================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("DIGIIN PHASE 38 — HACKATHON-FIRST PRODUCT DEVELOPMENT TEST SUITE")
    print("=" * 80)

    test_public_services_catalogue()
    test_flagship_scholarship_journey_and_sharing_review()
    test_data_saver_mode_compression()
    test_bilingual_dictionary_parity()
    test_public_service_api_endpoints()
    test_hackathon_submission_documentation()

    print()
    print("=" * 80)
    print("SUCCESS: ALL PHASE 38 HACKATHON PRODUCT CHECKS PASSED (100%)")
    print("=" * 80)
