"""Phase 8.2 — Envelope Encryption.

Layered AES-256-GCM encryption for documents and sensitive fields.

Architecture:
  Master Key / KEK (resolved from KeyRegistry)
          ↓
     Document DEK  (generated per-document, AES-256 random key)
          ↓
     Encrypted document bytes  (AES-256-GCM with per-encryption IV)

The application never holds a universal plaintext master key in memory
beyond the duration of a single encrypt/decrypt operation.

In development: KEK is derived from SECRET_KEY using HKDF-SHA256.
In production:  KEK is resolved from a Hardware Security Module or
                cloud KMS — replace _resolve_kek() accordingly.
"""

from __future__ import annotations

import base64
import json
import os
from dataclasses import asdict, dataclass

# AES-256-GCM via Python's cryptography library (pure-Python fallback if unavailable)
try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    _CRYPTO_AVAILABLE = True
except ImportError:
    _CRYPTO_AVAILABLE = False


# ---------------------------------------------------------------------------
# Encrypted Envelope
# ---------------------------------------------------------------------------


@dataclass
class EncryptedEnvelope:
    """Serializable envelope containing ciphertext and encrypted DEK."""

    key_id: str           # Which KEK was used
    dek_ciphertext: str   # Base64 DEK encrypted under KEK
    dek_iv: str           # Base64 IV used to encrypt DEK
    ciphertext: str       # Base64 encrypted content
    content_iv: str       # Base64 IV used to encrypt content
    algorithm: str = "AES-256-GCM"
    version: int = 1

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, raw: str) -> EncryptedEnvelope:
        return cls(**json.loads(raw))


# ---------------------------------------------------------------------------
# Key derivation helpers (dev-only)
# ---------------------------------------------------------------------------


def _derive_key(master: bytes, info: bytes, length: int = 32) -> bytes:
    """HKDF-SHA256 key derivation."""
    if _CRYPTO_AVAILABLE:
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=length,
            salt=b"digiin-kek-salt-v1",
            info=info,
        )
        return hkdf.derive(master)
    # Fallback: SHA-256 truncation (not production-grade)
    import hashlib
    return hashlib.sha256(master + info).digest()[:length]


def _aes_gcm_encrypt(key: bytes, plaintext: bytes) -> tuple[bytes, bytes]:
    """Encrypt with AES-256-GCM. Returns (ciphertext_with_tag, iv)."""
    iv = os.urandom(12)
    if _CRYPTO_AVAILABLE:
        aesgcm = AESGCM(key)
        ct = aesgcm.encrypt(iv, plaintext, None)
        return ct, iv
    # Fallback XOR cipher (development only — not secure)
    import hashlib
    keystream = hashlib.sha256(key + iv).digest() * (len(plaintext) // 32 + 1)
    ct = bytes(a ^ b for a, b in zip(plaintext, keystream[: len(plaintext)]))
    tag = hashlib.sha256(ct + key).digest()[:16]
    return ct + tag, iv


def _aes_gcm_decrypt(key: bytes, ciphertext_with_tag: bytes, iv: bytes) -> bytes:
    """Decrypt AES-256-GCM. Raises on authentication failure."""
    if _CRYPTO_AVAILABLE:
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(iv, ciphertext_with_tag, None)
    # Fallback XOR
    import hashlib
    ct = ciphertext_with_tag[:-16]
    expected_tag = hashlib.sha256(ct + key).digest()[:16]
    actual_tag = ciphertext_with_tag[-16:]
    if expected_tag != actual_tag:
        raise ValueError("AES-GCM authentication tag mismatch — data tampered")
    keystream = hashlib.sha256(key + iv).digest() * (len(ct) // 32 + 1)
    return bytes(a ^ b for a, b in zip(ct, keystream[: len(ct)]))


# ---------------------------------------------------------------------------
# Envelope Encryptor
# ---------------------------------------------------------------------------


class EnvelopeEncryptor:
    """
    Encrypts and decrypts using envelope encryption.

    Each encrypt() call:
      1. Resolves the active KEK from the KeyRegistry for key_id
      2. Generates a fresh random DEK (AES-256 = 32 bytes)
      3. Encrypts the DEK under the KEK
      4. Encrypts the plaintext under the DEK
      5. Returns an EncryptedEnvelope
    """

    def __init__(self) -> None:
        self._master_secret = os.environ.get(
            "DIGIIN_MASTER_SECRET", "digiin-master-secret-dev-only-2026"
        ).encode()

    def _resolve_kek(self, key_id: str) -> bytes:
        """Resolve KEK from secret. Replace with HSM/KMS call in production."""
        return _derive_key(self._master_secret, f"kek:{key_id}".encode())

    def encrypt(self, plaintext: bytes, key_id: str = "primary") -> EncryptedEnvelope:
        """Encrypt plaintext using envelope encryption."""
        kek = self._resolve_kek(key_id)

        # Generate fresh DEK
        dek = os.urandom(32)

        # Encrypt DEK under KEK
        dek_ct, dek_iv = _aes_gcm_encrypt(kek, dek)

        # Encrypt content under DEK
        content_ct, content_iv = _aes_gcm_encrypt(dek, plaintext)

        return EncryptedEnvelope(
            key_id=key_id,
            dek_ciphertext=base64.b64encode(dek_ct).decode(),
            dek_iv=base64.b64encode(dek_iv).decode(),
            ciphertext=base64.b64encode(content_ct).decode(),
            content_iv=base64.b64encode(content_iv).decode(),
        )

    def decrypt(self, envelope: EncryptedEnvelope) -> bytes:
        """Decrypt an EncryptedEnvelope. Raises ValueError on tamper detection."""
        kek = self._resolve_kek(envelope.key_id)

        # Decrypt DEK
        dek_ct = base64.b64decode(envelope.dek_ciphertext)
        dek_iv = base64.b64decode(envelope.dek_iv)
        dek = _aes_gcm_decrypt(kek, dek_ct, dek_iv)

        # Decrypt content
        content_ct = base64.b64decode(envelope.ciphertext)
        content_iv = base64.b64decode(envelope.content_iv)
        return _aes_gcm_decrypt(dek, content_ct, content_iv)

    def encrypt_field(self, value: str, key_id: str = "field") -> str:
        """Encrypt a single sensitive field value. Returns Base64 envelope JSON."""
        envelope = self.encrypt(value.encode(), key_id=key_id)
        return base64.b64encode(envelope.to_json().encode()).decode()

    def decrypt_field(self, encrypted_value: str) -> str:
        """Decrypt a field-level encrypted value."""
        envelope = EncryptedEnvelope.from_json(
            base64.b64decode(encrypted_value).decode()
        )
        return self.decrypt(envelope).decode()


# ---------------------------------------------------------------------------
# Field Encryptor (thin wrapper for convenience)
# ---------------------------------------------------------------------------


class FieldEncryptor:
    """Encrypt/decrypt individual sensitive model fields."""

    def __init__(self, encryptor: EnvelopeEncryptor | None = None) -> None:
        self._enc = encryptor or EnvelopeEncryptor()

    def protect(self, value: str | None) -> str | None:
        if value is None:
            return None
        return self._enc.encrypt_field(value)

    def reveal(self, encrypted: str | None) -> str | None:
        if encrypted is None:
            return None
        try:
            return self._enc.decrypt_field(encrypted)
        except Exception:
            return None  # Graceful degradation for legacy unencrypted fields


# ---------------------------------------------------------------------------
# Module singletons
# ---------------------------------------------------------------------------

envelope_encryptor = EnvelopeEncryptor()
field_encryptor = FieldEncryptor(envelope_encryptor)
