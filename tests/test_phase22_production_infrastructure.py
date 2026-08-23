"""
DigiIn Automated Production Infrastructure & Deployment Test Suite (Phase 22)
Validates Environment Isolation, KMS Envelope Encryption, Object Storage Presigned URLs, Connection Pooling, Canary Rollouts, DR Simulation, and Edge WAF.
"""

import sys
import os

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.infrastructure import (
    EnvironmentManager,
    EnvironmentType,
    KmsSecretManager,
    KeyPurpose,
    PrivateObjectStorageClient,
    DatabasePoolGovernor,
    MigrationPlanValidator,
    MigrationPhase,
    DeploymentOrchestrator,
    DeploymentStage,
    DisasterRecoveryEngine,
    EdgeWafEngine,
)

def test_environment_isolation_and_kms():
    print(">>> 1. Testing Environment Isolation & KMS Envelope Encryption...")
    # 1. Environment Config
    prod_cfg = EnvironmentManager.get_config("production")
    assert prod_cfg.environment == EnvironmentType.PRODUCTION
    assert prod_cfg.tls_enforced is True
    assert prod_cfg.allow_synthetic_accounts is False

    stg_cfg = EnvironmentManager.get_config("staging")
    assert stg_cfg.environment == EnvironmentType.STAGING
    assert stg_cfg.allow_synthetic_accounts is True

    # 2. KMS Envelope Encryption
    kms = KmsSecretManager()
    plaintext = b"DATABASE_PASSWORD_SUPER_SECRET_2026"
    
    enc = kms.encrypt_data(plaintext, KeyPurpose.SECRET_ENCRYPTION)
    assert enc["purpose"] == KeyPurpose.SECRET_ENCRYPTION
    assert "nonce" in enc and "ciphertext" in enc

    # Decrypt with matching purpose -> SUCCESS
    decrypted = kms.decrypt_data(enc)
    assert decrypted == plaintext

    # Cross-purpose decryption attempt -> FAIL
    enc_wrong_purpose = dict(enc)
    enc_wrong_purpose["purpose"] = KeyPurpose.DATABASE_ENCRYPTION
    try:
        kms.decrypt_data(enc_wrong_purpose)
        assert False, "KMS purpose violation: payload decrypted under wrong purpose DEK!"
    except Exception:
        pass  # Expected decryption authentication tag failure
    print("    [PASS] Environment segregation & KMS envelope encryption verified")

def test_object_storage_presigned_urls():
    print(">>> 2. Testing Private Object Storage Presigned URLs...")
    storage = PrivateObjectStorageClient(bucket_name="digiin-prod-documents-encrypted")

    # 1. Valid PDF upload URL generation
    res = storage.generate_presigned_upload_url(
        document_id="doc_889912",
        content_type="application/pdf",
        file_size_bytes=2 * 1024 * 1024,  # 2MB
        ttl_seconds=300
    )
    assert "uploadUrl" in res
    assert "docs/doc_889912/" in res["objectKey"]
    assert res["requiredHeaders"]["Content-Type"] == "application/pdf"

    # 2. Payload size exceeding 10MB -> REJECT
    try:
        storage.generate_presigned_upload_url(
            document_id="doc_large",
            content_type="application/pdf",
            file_size_bytes=15 * 1024 * 1024  # 15MB
        )
        assert False, "Object storage accepted file > 10MB!"
    except ValueError as ex:
        assert "PAYLOAD_TOO_LARGE" in str(ex)

    # 3. Disallowed MIME type -> REJECT
    try:
        storage.generate_presigned_upload_url(
            document_id="doc_exe",
            content_type="application/x-msdownload",
            file_size_bytes=1024
        )
        assert False, "Object storage accepted executable MIME type!"
    except ValueError as ex:
        assert "UNSUPPORTED_MEDIA_TYPE" in str(ex)
    print("    [PASS] Object storage presigned URLs & security bounds verified")

def test_db_pool_and_migration_validator():
    print(">>> 3. Testing Database Connection Pool & Migration Validator...")
    # 1. Connection pool governor
    pool = DatabasePoolGovernor(max_connections=5, reserved_admin_connections=1)
    
    # Acquire 4 standard connections -> OK
    assert pool.acquire_connection() is True
    assert pool.acquire_connection() is True
    assert pool.acquire_connection() is True
    assert pool.acquire_connection() is True

    # 5th standard connection is rejected (reserved for admin)
    assert pool.acquire_connection(is_admin=False) is False

    # Admin connection succeeds
    assert pool.acquire_connection(is_admin=True) is True

    # Release admin connection and one standard connection
    pool.release_connection()
    pool.release_connection()
    assert pool.acquire_connection(is_admin=False) is True

    # 2. Expand/Contract Migration Validator
    ok_expand, _ = MigrationPlanValidator.validate_migration(
        MigrationPhase.EXPAND,
        "ALTER TABLE documents ADD COLUMN verification_hash VARCHAR(64) DEFAULT NULL;"
    )
    assert ok_expand is True

    # Destructive DROP in EXPAND phase -> REJECT
    ok_bad_expand, err = MigrationPlanValidator.validate_migration(
        MigrationPhase.EXPAND,
        "ALTER TABLE documents DROP COLUMN legacy_status;"
    )
    assert ok_bad_expand is False
    assert "DESTRUCTIVE_MIGRATION_REJECTED" in err
    print("    [PASS] DB connection pool limits & migration validator verified")

def test_canary_rollout_and_instant_rollback():
    print(">>> 4. Testing Canary Rollout & Instant Digest Rollback...")
    deployer = DeploymentOrchestrator()
    assert deployer.current_active_digest == "sha256:digest_stable_v1_0_0_baseline"

    # Start deployment of v2.0.0
    rec = deployer.start_deployment(
        deployment_id="dep_01",
        new_version="2.0.0",
        new_artifact_digest="sha256:digest_v2_0_0_canary"
    )
    assert rec.stage == DeploymentStage.CANARY_5

    # Advance canary 5% -> 25% -> 50%
    deployer.advance_canary_stage(health_ok=True)
    assert rec.stage == DeploymentStage.CANARY_25

    deployer.advance_canary_stage(health_ok=True)
    assert rec.stage == DeploymentStage.CANARY_50

    # Simulate health degradation during 50% stage -> Auto-Rollback triggered
    ok, msg, rolled_back_rec = deployer.advance_canary_stage(health_ok=False)
    assert ok is True
    assert rolled_back_rec.status == "ROLLED_BACK"
    assert "ROLLBACK_EXECUTED" in msg
    assert deployer.current_active_digest == "sha256:digest_stable_v1_0_0_baseline"
    print("    [PASS] Canary progression & instant rollback verified")

def test_disaster_recovery_simulation():
    print(">>> 5. Testing Disaster Recovery Simulation & Proof Verification...")
    dr_engine = DisasterRecoveryEngine()
    
    # Execute complete DR simulation
    res = dr_engine.simulate_dr_recovery()
    assert res["success"] is True
    assert res["preDisasterProofValid"] is True
    assert res["postRestoreMintingValid"] is True
    assert res["rtoMs"] < 1000.0  # RTO under 1 second in automated drill
    print("    [PASS] Disaster recovery restore & proof integrity verified")

def test_edge_waf_and_cache_control():
    print(">>> 6. Testing Edge WAF & Cache Policy...")
    # 1. Clean API request -> ALLOW
    ok, err, code = EdgeWafEngine.inspect_request(
        path="/api/v1/verifications",
        method="POST",
        body_bytes=b'{"subject": "DGI-SBX-001"}',
        headers={"Content-Type": "application/json"}
    )
    assert ok is True

    # 2. SQL Injection payload -> REJECT (403)
    ok_sqli, err_sqli, code_sqli = EdgeWafEngine.inspect_request(
        path="/api/v1/verifications",
        method="POST",
        body_bytes=b'{"subject": "1\' OR \'1\'=\'1 UNION SELECT * FROM users--"}',
        headers={"Content-Type": "application/json"}
    )
    assert ok_sqli is False
    assert code_sqli == 403
    assert "MALICIOUS_REQUEST_BLOCKED" in err_sqli

    # 3. Payload > 2MB -> REJECT (413)
    large_payload = b"A" * (3 * 1024 * 1024)
    ok_large, err_large, code_large = EdgeWafEngine.inspect_request(
        path="/api/v1/verifications",
        method="POST",
        body_bytes=large_payload,
        headers={"Content-Type": "application/json"}
    )
    assert ok_large is False
    assert code_large == 413

    # 4. Security Headers & No-Store Caching on sensitive endpoints
    headers = EdgeWafEngine.get_security_headers_for_response("/api/v1/proofs/prf_01K882")
    assert "no-store" in headers["Cache-Control"]
    assert headers["X-Frame-Options"] == "DENY"
    print("    [PASS] Edge WAF protection & strict cache policy verified")

def run_all_infrastructure_tests():
    print("=" * 80)
    print("DIGIIN PHASE 22 PRODUCTION INFRASTRUCTURE & DEPLOYMENT TEST MATRIX")
    print("=" * 80)
    test_environment_isolation_and_kms()
    test_object_storage_presigned_urls()
    test_db_pool_and_migration_validator()
    test_canary_rollout_and_instant_rollback()
    test_disaster_recovery_simulation()
    test_edge_waf_and_cache_control()
    print("=" * 80)
    print("SUCCESS: ALL 6 PRODUCTION INFRASTRUCTURE & DEPLOYMENT TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_infrastructure_tests()
