"""
DigiIn Automated Security & Production Hardening Test Suite (Phase 16)
Validates centralized authentication, RBAC, IDOR defense, file security, rate limiting, and session security.
"""

import sys
import os

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.security_foundation.auth_security import AuthenticationSecurityService, AccountState
from app.core.security_foundation.authorization import AuthorizationService, Role, Permission
from app.core.security_foundation.file_security import FileSecurityService
from app.core.security_foundation.rate_limiting import RateLimiterService
from app.core.security_foundation.error_handling import DigiInErrorCode, format_error_response

def test_password_hashing_and_lockout():
    print(">>> 1. Testing Password Hashing & Lockout Defense...")
    auth = AuthenticationSecurityService(max_failed_attempts=3, lockout_duration_seconds=60)
    password = "SuperSecurePassword123!"
    hashed = auth.hash_password(password)

    assert hashed.startswith("pbkdf2_sha256$100000$"), "Invalid hash format"
    assert auth.verify_password(password, hashed) is True, "Failed to verify valid password"
    assert auth.verify_password("WrongPassword", hashed) is False, "Verified invalid password"

    # Test lockout after 3 failed attempts
    user_id = "citizen_rahul_99"
    auth.record_login_attempt(user_id, success=False)
    auth.record_login_attempt(user_id, success=False)
    allowed, msg = auth.record_login_attempt(user_id, success=False)
    assert allowed is False
    assert "ACCOUNT_LOCKED" in msg
    assert auth.is_locked_out(user_id) is True
    print("    [PASS] Password hashing & account lockout verified")

def test_session_security_and_revocation():
    print(">>> 2. Testing Session Security & Remote Revocation...")
    auth = AuthenticationSecurityService()
    user_id = "user_42"
    session = auth.create_session(user_id, user_agent="Mozilla/5.0", ip_address="192.168.1.100")
    session_id = session["session_id"]

    assert auth.validate_session(session_id) is not None, "Valid session rejected"
    
    # Revoke session
    assert auth.revoke_session(session_id) is True, "Failed to revoke session"
    assert auth.validate_session(session_id) is None, "Revoked session still valid"
    print("    [PASS] Session lifecycle & revocation verified")

def test_totp_mfa_verification():
    print(">>> 3. Testing TOTP MFA Setup & Validation...")
    auth = AuthenticationSecurityService()
    user_id = "user_mfa_test"
    secret = auth.setup_totp_mfa(user_id)
    assert len(secret) == 40, "Invalid MFA secret length"
    
    # Verification with invalid code
    assert auth.verify_totp_code(user_id, "000000") is False, "Accepted invalid MFA code"
    print("    [PASS] TOTP MFA security verified")

def test_rbac_and_idor_defense():
    print(">>> 4. Testing RBAC Permissions & IDOR Defense...")
    citizen_actor = {"user_id": "citizen_100", "role": Role.CITIZEN}
    other_citizen_actor = {"user_id": "citizen_200", "role": Role.CITIZEN}
    org_actor = {"user_id": "user_org_1", "organisation_id": "ORG_DELHI_UNIV", "role": Role.ORG_USER}
    other_org_actor = {"user_id": "user_org_2", "organisation_id": "ORG_MUMBAI_UNIV", "role": Role.ORG_USER}

    doc_resource = {"id": "doc_1", "citizen_id": "citizen_100"}
    req_resource = {"id": "req_1", "organisation_id": "ORG_DELHI_UNIV"}

    # Citizen A accessing own doc -> ALLOW
    allowed, err = AuthorizationService.authorize_resource_access(citizen_actor, Permission.DOCUMENT_READ, doc_resource)
    assert allowed is True, f"Citizen denied own doc: {err}"

    # Citizen B accessing Citizen A's doc -> DENY (IDOR)
    allowed, err = AuthorizationService.authorize_resource_access(other_citizen_actor, Permission.DOCUMENT_READ, doc_resource)
    assert allowed is False, "Citizen B accessed Citizen A doc (IDOR leak!)"
    assert "FORBIDDEN_IDOR" in err

    # Org A accessing own request -> ALLOW
    allowed, err = AuthorizationService.authorize_resource_access(org_actor, Permission.VERIFICATION_READ, req_resource)
    assert allowed is True, f"Org A denied own request: {err}"

    # Org B accessing Org A's request -> DENY (Tenant Isolation)
    allowed, err = AuthorizationService.authorize_resource_access(other_org_actor, Permission.VERIFICATION_READ, req_resource)
    assert allowed is False, "Org B accessed Org A request (Tenant isolation breach!)"
    assert "FORBIDDEN_TENANT_ISOLATION" in err
    print("    [PASS] RBAC & IDOR resource ownership enforcement verified")

def test_file_security_and_magic_bytes():
    print(">>> 5. Testing File Security & Magic-Byte Validation...")
    # Genuine PDF
    pdf_content = b"%PDF-1.4 sample document bytes here"
    valid, mime, err = FileSecurityService.validate_file_content("certificate.pdf", pdf_content)
    assert valid is True
    assert mime == "application/pdf"

    # Spoofed PDF (executable payload disguised as .pdf)
    spoofed_content = b"MZ\x90\x00\x03\x00\x00\x00 executable bytes"
    valid, mime, err = FileSecurityService.validate_file_content("malicious.pdf", spoofed_content)
    assert valid is False, "Accepted spoofed file disguised as PDF"
    assert "MAGIC_BYTE_MISMATCH" in err or "EXTENSION_SPOOF" in err

    # Secure storage key generation (unguessable UUID path)
    key = FileSecurityService.generate_secure_storage_key("citizen_100", ".pdf")
    assert key.startswith("vault/"), "Storage key missing vault prefix"
    assert key.endswith(".pdf"), "Storage key missing correct extension"

    # Short-lived signed access token
    secret = "digiin_super_secret_storage_key_32_bytes"
    token = FileSecurityService.generate_signed_access_token(key, "citizen_100", secret, ttl_seconds=300)
    assert FileSecurityService.verify_signed_access_token(key, "citizen_100", token, secret) is True
    assert FileSecurityService.verify_signed_access_token(key, "citizen_200", token, secret) is False
    print("    [PASS] Magic-byte validation & private storage signed tokens verified")

def test_rate_limiting_enforcement():
    print(">>> 6. Testing Tiered Rate Limiting...")
    limiter = RateLimiterService()
    client_ip = "203.0.113.42"

    # OTP tier has limit of 3 requests / min
    assert limiter.check_rate_limit(client_ip, "OTP")[0] is True
    assert limiter.check_rate_limit(client_ip, "OTP")[0] is True
    assert limiter.check_rate_limit(client_ip, "OTP")[0] is True
    
    # 4th request must be blocked
    allowed, remaining, retry_after = limiter.check_rate_limit(client_ip, "OTP")
    assert allowed is False, "Rate limiter failed to block 4th OTP attempt"
    assert remaining == 0
    assert retry_after > 0
    print("    [PASS] Tiered token bucket rate limiting verified")

def test_error_response_sanitization():
    print(">>> 7. Testing Error Response Sanitization & Request IDs...")
    resp = format_error_response(
        DigiInErrorCode.CONSENT_REQUIRED,
        "Valid citizen consent is required before accessing this verification record.",
        "req_01J82A91MX"
    )
    assert resp["error"]["code"] == "CONSENT_REQUIRED"
    assert resp["error"]["requestId"] == "req_01J82A91MX"
    assert "stack" not in resp["error"], "Stack trace leaked in error response"
    print("    [PASS] Error response sanitization verified")

def run_all_security_tests():
    print("=" * 80)
    print("DIGIIN PHASE 16 PRODUCTION SECURITY & HARDENING TEST MATRIX")
    print("=" * 80)
    test_password_hashing_and_lockout()
    test_session_security_and_revocation()
    test_totp_mfa_verification()
    test_rbac_and_idor_defense()
    test_file_security_and_magic_bytes()
    test_rate_limiting_enforcement()
    test_error_response_sanitization()
    print("=" * 80)
    print("SUCCESS: ALL 7 CORE SECURITY & HARDENING TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_security_tests()
