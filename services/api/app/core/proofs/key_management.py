"""
DigiIn Cryptographic Proof Subsystem — Key Lifecycle Management & Rotation
Supports key states (ACTIVE, ROTATING, RETIRED, REVOKED) allowing legacy proofs to remain verifiable.
"""

from __future__ import annotations

import base64
import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)


class KeyStatus:
    ACTIVE = "ACTIVE"
    ROTATING = "ROTATING"
    RETIRED = "RETIRED"
    REVOKED = "REVOKED"

class SigningKey:
    def __init__(
        self,
        key_id: str,
        private_bytes: bytes,
        public_bytes: bytes,
        algorithm: str = "Ed25519",
        status: str = KeyStatus.ACTIVE,
        created_at: float | None = None,
        expires_at: float | None = None
    ):
        self.key_id = key_id
        self._private_bytes = private_bytes
        self.public_bytes = public_bytes
        self.algorithm = algorithm
        self.status = status
        self.created_at = created_at or time.time()
        self.expires_at = expires_at

    @property
    def public_key_base64(self) -> str:
        return base64.urlsafe_b64encode(self.public_bytes).rstrip(b"=").decode("utf-8")

    @property
    def private_key_bytes(self) -> bytes:
        return self._private_bytes

class KeyManager:
    def __init__(self):
        self._keys: dict[str, SigningKey] = {}
        self._active_key_id: str | None = None

    def generate_and_register_key(self, key_id: str, status: str = KeyStatus.ACTIVE) -> SigningKey:
        """Generate a new Ed25519 keypair and register in the key store."""
        private = Ed25519PrivateKey.generate()
        priv_bytes = private.private_bytes(
            Encoding.Raw,
            PrivateFormat.Raw,
            NoEncryption(),
        )
        pub_bytes = private.public_key().public_bytes(
            Encoding.Raw,
            PublicFormat.Raw,
        )
        key = SigningKey(key_id=key_id, private_bytes=priv_bytes, public_bytes=pub_bytes, status=status)
        self._keys[key_id] = key
        if status == KeyStatus.ACTIVE:
            self._active_key_id = key_id
        return key

    def get_active_signing_key(self) -> SigningKey | None:
        if self._active_key_id:
            return self._keys.get(self._active_key_id)
        return None

    def get_key(self, key_id: str) -> SigningKey | None:
        return self._keys.get(key_id)

    def rotate_key(self, new_key_id: str) -> SigningKey:
        """Rotate active key: current ACTIVE key transitions to RETIRED, new key becomes ACTIVE."""
        if self._active_key_id and self._active_key_id in self._keys:
            self._keys[self._active_key_id].status = KeyStatus.RETIRED

        new_key = self.generate_and_register_key(new_key_id, status=KeyStatus.ACTIVE)
        self._active_key_id = new_key_id
        return new_key

    def revoke_key(self, key_id: str) -> bool:
        key = self._keys.get(key_id)
        if key:
            key.status = KeyStatus.REVOKED
            if self._active_key_id == key_id:
                self._active_key_id = None
            return True
        return False
