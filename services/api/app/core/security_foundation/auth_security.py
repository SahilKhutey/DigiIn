"""
DigiIn Core Security Subsystem — Authentication & Session Hardening
Implements password hashing, brute-force lockout, TOTP MFA, and session security.
"""

import base64
import hashlib
import hmac
import secrets
import time


class AccountState:
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"

class AuthenticationSecurityService:
    def __init__(self, max_failed_attempts: int = 5, lockout_duration_seconds: int = 900):
        self.max_failed_attempts = max_failed_attempts
        self.lockout_duration_seconds = lockout_duration_seconds
        self._login_attempts: dict[str, list] = {}
        self._sessions: dict[str, dict] = {}
        self._mfa_secrets: dict[str, str] = {}

    def hash_password(self, password: str, salt: str | None = None) -> str:
        """Derive secure cryptographic password hash using PBKDF2-HMAC-SHA256 with random salt."""
        if not salt:
            salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"pbkdf2_sha256$100000${salt}${base64.b64encode(key).decode('utf-8')}"

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against stored hash with timing-safe comparison."""
        try:
            parts = hashed.split('$')
            if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
                return False
            iterations = int(parts[1])
            salt = parts[2]
            stored_key = base64.b64decode(parts[3])
            computed_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                iterations
            )
            return hmac.compare_digest(stored_key, computed_key)
        except Exception:
            return False

    def record_login_attempt(self, identifier: str, success: bool) -> tuple[bool, str | None]:
        """Record login attempt and enforce automatic account lockout."""
        now = time.time()
        attempts = self._login_attempts.setdefault(identifier, [])
        # Expire older attempts outside window
        self._login_attempts[identifier] = [t for t in attempts if now - t < self.lockout_duration_seconds]

        if success:
            self._login_attempts[identifier] = []
            return True, None

        self._login_attempts[identifier].append(now)
        if len(self._login_attempts[identifier]) >= self.max_failed_attempts:
            return False, "ACCOUNT_LOCKED: Maximum failed login attempts exceeded. Try again in 15 minutes."

        remaining = self.max_failed_attempts - len(self._login_attempts[identifier])
        return False, f"AUTH_FAILED: Invalid credentials. {remaining} attempt(s) remaining."

    def is_locked_out(self, identifier: str) -> bool:
        now = time.time()
        attempts = self._login_attempts.get(identifier, [])
        valid_attempts = [t for t in attempts if now - t < self.lockout_duration_seconds]
        return len(valid_attempts) >= self.max_failed_attempts

    def create_session(self, user_id: str, user_agent: str, ip_address: str, ttl_seconds: int = 86400) -> dict:
        """Create a cryptographically secure, fingerprinted session."""
        session_id = f"sess_{secrets.token_urlsafe(32)}"
        now = time.time()
        ip_hash = hashlib.sha256(ip_address.encode('utf-8')).hexdigest()[:16]
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": now,
            "last_seen_at": now,
            "expires_at": now + ttl_seconds,
            "user_agent": user_agent,
            "ip_hash": ip_hash,
            "revoked": False
        }
        self._sessions[session_id] = session
        return session

    def validate_session(self, session_id: str) -> dict | None:
        """Validate session existence, active status, and expiry."""
        session = self._sessions.get(session_id)
        if not session or session.get("revoked") or time.time() > session.get("expires_at", 0):
            return None
        session["last_seen_at"] = time.time()
        return session

    def revoke_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            self._sessions[session_id]["revoked"] = True
            return True
        return False

    def revoke_all_user_sessions(self, user_id: str, keep_session_id: str | None = None) -> int:
        revoked_count = 0
        for s_id, s in self._sessions.items():
            if s.get("user_id") == user_id and s_id != keep_session_id:
                s["revoked"] = True
                revoked_count += 1
        return revoked_count

    def setup_totp_mfa(self, user_id: str) -> str:
        """Generate a secure TOTP secret key for MFA enrollment."""
        secret = secrets.token_hex(20)
        self._mfa_secrets[user_id] = secret
        return secret

    def verify_totp_code(self, user_id: str, code: str) -> bool:
        """Verify dynamic 6-digit TOTP code against registered secret."""
        secret = self._mfa_secrets.get(user_id)
        if not secret or len(code) != 6 or not code.isdigit():
            return False
        # Calculate counter based on 30s window
        time_step = int(time.time() / 30)
        for offset in [-1, 0, 1]:  # Allow 1-step clock skew
            counter = (time_step + offset).to_bytes(8, byteorder='big')
            hmac_digest = hmac.new(bytes.fromhex(secret), counter, hashlib.sha1).digest()
            offset_idx = hmac_digest[-1] & 0x0F
            binary_code = (
                ((hmac_digest[offset_idx] & 0x7F) << 24) |
                ((hmac_digest[offset_idx + 1] & 0xFF) << 16) |
                ((hmac_digest[offset_idx + 2] & 0xFF) << 8) |
                (hmac_digest[offset_idx + 3] & 0xFF)
            )
            expected_code = str(binary_code % 1000000).zfill(6)
            if hmac.compare_digest(expected_code, code):
                return True
        return False
