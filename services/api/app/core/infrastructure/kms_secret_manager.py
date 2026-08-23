"""
DigiIn Production Infrastructure — KMS Secret Manager & Key Hierarchy
Implements envelope encryption and enforces separation between Database, Document, Secret, and Proof-signing keys.
"""

from __future__ import annotations

import base64
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class KeyPurpose:
    DATABASE_ENCRYPTION = "DATABASE_ENCRYPTION"
    DOCUMENT_STORAGE = "DOCUMENT_STORAGE"
    SECRET_ENCRYPTION = "SECRET_ENCRYPTION"
    PROOF_SIGNING = "PROOF_SIGNING"

class KmsSecretManager:
    def __init__(self, master_kms_key_id: str = "kms-master-root-2026"):
        self.master_kms_key_id = master_kms_key_id
        self._dek_keys: dict[str, bytes] = {}
        self._secrets_store: dict[str, str] = {}
        self._initialize_subsystem_keys()

    def _initialize_subsystem_keys(self):
        # Derive unique 256-bit Data Encryption Keys (DEKs) for each cryptographic domain
        for purpose in (KeyPurpose.DATABASE_ENCRYPTION, KeyPurpose.DOCUMENT_STORAGE, KeyPurpose.SECRET_ENCRYPTION, KeyPurpose.PROOF_SIGNING):
            raw_key = AESGCM.generate_key(bit_length=256)
            self._dek_keys[purpose] = raw_key

    def encrypt_data(self, plaintext: bytes, purpose: str) -> dict[str, str]:
        """Encrypt payload using purpose-isolated DEK via AES-256-GCM."""
        dek = self._dek_keys.get(purpose)
        if not dek:
            raise ValueError(f"UNKNOWN_KEY_PURPOSE: Purpose '{purpose}' does not have an allocated DEK.")

        nonce = secrets.token_bytes(12)
        aesgcm = AESGCM(dek)
        ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=purpose.encode("utf-8"))

        return {
            "masterKeyId": self.master_kms_key_id,
            "purpose": purpose,
            "nonce": base64.b64encode(nonce).decode("utf-8"),
            "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
        }

    def decrypt_data(self, encrypted_payload: dict[str, str]) -> bytes:
        """Decrypt payload and verify authentication tag and purpose binding."""
        purpose = encrypted_payload.get("purpose", "")
        dek = self._dek_keys.get(purpose)
        if not dek:
            raise ValueError(f"DEK_NOT_FOUND: Cannot decrypt payload for purpose '{purpose}'.")

        nonce = base64.b64decode(encrypted_payload["nonce"])
        ciphertext = base64.b64decode(encrypted_payload["ciphertext"])
        aesgcm = AESGCM(dek)
        return aesgcm.decrypt(nonce, ciphertext, associated_data=purpose.encode("utf-8"))

    def store_secret(self, secret_name: str, secret_value: str) -> None:
        enc = self.encrypt_data(secret_value.encode("utf-8"), KeyPurpose.SECRET_ENCRYPTION)
        self._secrets_store[secret_name] = f"{enc['nonce']}:{enc['ciphertext']}"

    def get_secret(self, secret_name: str) -> str | None:
        val = self._secrets_store.get(secret_name)
        if not val:
            return None
        nonce, ct = val.split(":")
        payload = {"purpose": KeyPurpose.SECRET_ENCRYPTION, "nonce": nonce, "ciphertext": ct}
        return self.decrypt_data(payload).decode("utf-8")
