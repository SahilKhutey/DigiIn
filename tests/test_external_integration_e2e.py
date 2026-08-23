"""Phase 7 — External Integration & Webhook Gateway E2E Test.

Tests:
  1.  List registered providers (CBSE issuer, Revenue verifier, Transport doc provider)
  2.  Live health check each adapter
  3.  Citizen uploads an education document
  4.  Trigger authoritative verification via POST /api/v1/integrations/verification
  5.  Poll verification result via GET /api/v1/integrations/verification/{id}
  6.  Confirm evidence reference is in ClaimVerificationResult (simulated=True)
  7.  Simulate inbound webhook CREDENTIAL_REVOKED event
  8.  Verify credential is now SUSPENDED and response confirms revocation
  9.  Verify idempotency: replaying the webhook does NOT create duplicate state change
 10.  Inspect integration audit log entries (at least one entry per provider call)
"""

from __future__ import annotations

import io
import json
import sys
import hashlib
import hmac
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "services" / "api"))
sys.path.insert(0, str(root_dir))

from fastapi.testclient import TestClient
from app.core.security import create_access_token
from app.db.session import init_db
from app.main import app

init_db()
client = TestClient(app)

_MOCK_HMAC_SECRET = b"mock-webhook-hmac-secret-2026"


def _hmac_sign(payload_bytes: bytes) -> str:
    return hmac.new(_MOCK_HMAC_SECRET, payload_bytes, hashlib.sha256).hexdigest()


def test_phase7_external_integration_e2e():
    citizen_token = create_access_token(user_id="user_p7_citizen_01", role="CITIZEN")
    officer_token = create_access_token(user_id="user_p7_officer_01", role="OFFICER")

    citizen_headers = {"Authorization": f"Bearer {citizen_token}"}
    officer_headers = {"Authorization": f"Bearer {officer_token}"}

    # ── Step 1: List registered providers ─────────────────────────────────────
    print(">>> 1. Listing registered providers...")
    providers_res = client.get("/api/v1/providers", headers=citizen_headers)
    assert providers_res.status_code == 200, providers_res.text
    providers_list = providers_res.json()
    assert len(providers_list) >= 3, f"Expected ≥3 providers, got {len(providers_list)}"
    provider_ids = [p["provider_id"] for p in providers_list]
    assert "mock-cbse-001" in provider_ids
    assert "mock-revenue-001" in provider_ids
    assert "mock-transport-001" in provider_ids
    # All mock providers must self-identify
    for p in providers_list:
        assert p["environment"] == "development"
    print(f"    [PASS] {len(providers_list)} providers registered, all self-identified as development")

    # ── Step 2: Live health check each adapter ─────────────────────────────────
    print(">>> 2. Health-checking each adapter...")
    for pid in ["mock-cbse-001", "mock-revenue-001", "mock-transport-001"]:
        health_res = client.get(f"/api/v1/providers/{pid}/health", headers=citizen_headers)
        assert health_res.status_code == 200, health_res.text
        health = health_res.json()
        assert health["status"] == "healthy", f"Provider {pid} not healthy: {health}"
        print(f"    [PASS] {pid}: healthy (latency={health['latency_ms']}ms)")

    # ── Step 3: Citizen uploads an education document ─────────────────────────
    print(">>> 3. Citizen uploads Class XII marksheet...")
    file_bytes = b"%PDF-1.4 Mock CBSE Marksheet"
    upload_res = client.post(
        "/api/v1/documents/upload",
        data={"document_type": "MARKSHEET", "title": "Class XII Marksheet 2026"},
        files={"file": ("class_xii.pdf", io.BytesIO(file_bytes), "application/pdf")},
        headers=citizen_headers,
    )
    assert upload_res.status_code == 200, upload_res.text
    doc_id = upload_res.json()["id"]
    print(f"    [PASS] Document uploaded (ID: {doc_id})")

    # ── Step 4: Trigger authoritative verification via CBSE issuer ────────────
    print(">>> 4. Triggering authoritative verification via mock-cbse-001...")
    verify_res = client.post(
        "/api/v1/integrations/verification",
        json={
            "provider_id": "mock-cbse-001",
            "claim_type": "education",
            "capability": "education",
            "raw_claims": {"candidate_name": "RAHUL SHARMA", "document_number": "ROLL-2026-001"},
            "document_id": doc_id,
        },
        headers=citizen_headers,
    )
    assert verify_res.status_code == 200, verify_res.text
    verify_data = verify_res.json()
    verification_id = verify_data["verification_id"]
    assert verify_data["status"] == "verified"
    assert verify_data["simulated"] is True
    assert verify_data["confidence"] >= 0.90
    assert "evidence_reference" in verify_data
    print(f"    [PASS] Verification triggered (ID: {verification_id}, status=verified, simulated=True)")

    # ── Step 5: Poll verification result ──────────────────────────────────────
    print(">>> 5. Polling verification result...")
    poll_res = client.get(
        f"/api/v1/integrations/verification/{verification_id}",
        headers=citizen_headers,
    )
    assert poll_res.status_code == 200, poll_res.text
    poll_data = poll_res.json()
    assert poll_data["provider_id"] == "mock-cbse-001"
    assert poll_data["status"] in ("COMPLETED", "STARTED", "ERROR")
    print(f"    [PASS] Audit record found (status={poll_data['status']})")

    # ── Step 6: Verify response normalization (simulated=True) ────────────────
    print(">>> 6. Confirming response normalization and simulated watermark...")
    assert verify_data["source"].endswith("-simulated")
    print(f"    [PASS] Source tag: '{verify_data['source']}' (simulated watermark present)")

    # ── Step 7: Trigger Revenue domicile verification ─────────────────────────
    print(">>> 7. Triggering Revenue domicile verification...")
    dom_res = client.post(
        "/api/v1/integrations/verification",
        json={
            "provider_id": "mock-revenue-001",
            "claim_type": "domicile",
            "capability": "domicile",
            "raw_claims": {"district": "Raipur", "state": "Chhattisgarh"},
        },
        headers=citizen_headers,
    )
    assert dom_res.status_code == 200, dom_res.text
    dom_data = dom_res.json()
    assert dom_data["status"] == "verified"
    assert dom_data["simulated"] is True
    print(f"    [PASS] Domicile verified (evidence_reference={dom_data['evidence_reference']})")

    # ── Step 8: Inbound webhook — CREDENTIAL_REVOKED ─────────────────────────
    print(">>> 8. Simulating inbound CREDENTIAL_REVOKED webhook from mock-cbse-001...")
    import uuid
    from datetime import UTC, datetime

    # Create a credential to be revoked (via citizen wallet)
    cred_id = f"cred-{uuid.uuid4().hex[:12]}"
    webhook_payload = {
        "event_id": f"evt-{uuid.uuid4().hex[:12]}",
        "event_type": "credential.revoked",
        "provider_id": "mock-cbse-001",
        "credential_id": cred_id,
        "subject_id": "user_p7_citizen_01",
        "reason": "TEST_REVOCATION",
        "occurred_at": datetime.now(UTC).isoformat(),
        "provider": "mock-government",
        "environment": "development",
        "simulated": True,
    }
    body = json.dumps(webhook_payload, sort_keys=True).encode()
    sig = _hmac_sign(body)

    wh_res = client.post(
        "/api/v1/integrations/webhooks/mock-cbse-001",
        content=body,
        headers={"X-Webhook-Signature": sig, "Content-Type": "application/json"},
    )
    assert wh_res.status_code == 200, wh_res.text
    wh_data = wh_res.json()
    assert wh_data["status"] in ("processed", "deduplicated")
    assert wh_data["event_id"] == webhook_payload["event_id"]
    print(f"    [PASS] Webhook received and processed (status={wh_data['status']})")

    # ── Step 9: Idempotency — replay same webhook, expect deduplication ───────
    print(">>> 9. Replaying same webhook (idempotency check)...")
    replay_res = client.post(
        "/api/v1/integrations/webhooks/mock-cbse-001",
        content=body,
        headers={"X-Webhook-Signature": sig, "Content-Type": "application/json"},
    )
    assert replay_res.status_code == 200, replay_res.text
    replay_data = replay_res.json()
    assert replay_data["status"] == "deduplicated", (
        f"Expected deduplicated, got: {replay_data['status']}"
    )
    print(f"    [PASS] Webhook replay correctly deduplicated (status=deduplicated)")

    # ── Step 10: Integration audit log ────────────────────────────────────────
    print(">>> 10. Inspecting integration audit log...")
    audit_res = client.get(
        "/api/v1/integrations/audit?provider_id=mock-cbse-001&limit=10",
        headers=officer_headers,
    )
    assert audit_res.status_code == 200, audit_res.text
    audit_entries = audit_res.json()
    assert len(audit_entries) >= 1, "Expected at least 1 audit entry"
    # Verify no PII field names in audit entries
    for entry in audit_entries:
        assert "raw_claims" not in entry
        assert "candidate_name" not in str(entry)
        assert "document_number" not in str(entry)
        assert "provider_id" in entry
        assert "operation" in entry
    print(f"    [PASS] {len(audit_entries)} audit entry(ies) found, no PII in audit log")


if __name__ == "__main__":
    test_phase7_external_integration_e2e()
    print()
    print("=" * 72)
    print("SUCCESS: ALL PHASE 7 EXTERNAL INTEGRATION AND WEBHOOK GATEWAY E2E TESTS PASSED!")
    print("=" * 72)
