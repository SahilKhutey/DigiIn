"""
DigiIn Core Security Subsystem — File Security & Quarantine Engine
Validates magic bytes, enforces size and compression limits, sanitizes storage keys, and controls private storage access.
"""

import hashlib
import hmac
import os
import secrets
import time

# Magic Byte Signatures for allowed MIME types
MAGIC_SIGNATURES = {
    "application/pdf": [b"%PDF-"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/jpeg": [b"\xff\xd8\xff"],
}

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

class FileSecurityService:
    @staticmethod
    def validate_file_content(filename: str, content: bytes) -> tuple[bool, str | None, str | None]:
        """
        Validate file extension, size limit, and genuine magic-byte signatures.
        Rejects extension spoofing (e.g. executable renamed to .pdf).
        """
        # 1. Size Validation
        if len(content) == 0:
            return False, None, "INVALID_FILE: File payload cannot be empty."
        if len(content) > MAX_FILE_SIZE_BYTES:
            return False, None, f"FILE_TOO_LARGE: Exceeds maximum allowed limit of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB."

        # 2. Extension check
        _, ext = os.path.splitext(filename.lower())
        if ext not in ALLOWED_EXTENSIONS:
            return False, None, f"INVALID_EXTENSION: Extension '{ext}' is not permitted."

        # 3. Magic Byte Signature Validation
        detected_mime = None
        for mime, signatures in MAGIC_SIGNATURES.items():
            for sig in signatures:
                if content.startswith(sig):
                    detected_mime = mime
                    break
            if detected_mime:
                break

        if not detected_mime:
            return False, None, "MAGIC_BYTE_MISMATCH: File header signature does not match allowed types (PDF/PNG/JPEG)."

        # 4. Confirm extension aligns with detected MIME
        if ext == ".pdf" and detected_mime != "application/pdf":
            return False, None, "EXTENSION_SPOOF_DETECTED: .pdf file does not contain valid PDF header."
        if ext in (".jpg", ".jpeg") and detected_mime != "image/jpeg":
            return False, None, "EXTENSION_SPOOF_DETECTED: JPEG file does not contain valid JPEG header."
        if ext == ".png" and detected_mime != "image/png":
            return False, None, "EXTENSION_SPOOF_DETECTED: PNG file does not contain valid PNG header."

        return True, detected_mime, None

    @staticmethod
    def generate_secure_storage_key(user_id: str, extension: str) -> str:
        """
        Generate unguessable UUID-based storage key. Never construct storage paths from user filenames.
        Prevents path traversal and directory enumeration.
        """
        clean_ext = extension.lower() if extension.startswith('.') else f".{extension.lower()}"
        random_id = secrets.token_hex(16)
        user_hash = hashlib.sha256(user_id.encode('utf-8')).hexdigest()[:12]
        return f"vault/{user_hash}/{random_id}{clean_ext}"

    @staticmethod
    def calculate_checksum(content: bytes) -> str:
        """Calculate SHA-256 binary checksum for document integrity."""
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def generate_signed_access_token(storage_key: str, user_id: str, secret_key: str, ttl_seconds: int = 300) -> str:
        """Generate short-lived cryptographic signed URL token for private object storage."""
        expires_at = int(time.time()) + ttl_seconds
        payload = f"{storage_key}:{user_id}:{expires_at}"
        signature = hmac.new(
            secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"{expires_at}.{signature}"

    @staticmethod
    def verify_signed_access_token(storage_key: str, user_id: str, token: str, secret_key: str) -> bool:
        """Verify signed access token integrity and expiration."""
        try:
            parts = token.split('.')
            if len(parts) != 2:
                return False
            expires_at = int(parts[0])
            provided_sig = parts[1]

            if time.time() > expires_at:
                return False  # Token expired

            payload = f"{storage_key}:{user_id}:{expires_at}"
            expected_sig = hmac.new(
                secret_key.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(provided_sig, expected_sig)
        except Exception:
            return False
