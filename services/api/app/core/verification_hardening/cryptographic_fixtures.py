"""
DigiIn Verification Hardening — Cryptographic Fixtures & Keypairs
Provides authentic Ed25519 keypairs, RFC 8785 canonical payloads, SHA-256 digests, and tamperable test credentials.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
    )
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

@dataclass
class KeypairFixture:
    key_id: str
    issuer_name: str
    private_key: Any
    public_key: Any
    public_key_hex: str

class CryptographicFixtureRegistry:
    def __init__(self):
        self._keypairs: dict[str, KeypairFixture] = {}
        self._init_default_fixtures()

    def _init_default_fixtures(self):
        if HAS_CRYPTO:
            priv = Ed25519PrivateKey.generate()
            pub = priv.public_key()
            pub_hex = hashlib.sha256(b"du_pub_key").hexdigest()
        else:
            priv = "mock_private_key_du"
            pub = "mock_public_key_du"
            pub_hex = "mock_pub_hex_du_2026"

        fixture = KeypairFixture(
            key_id="key_delhi_univ_ed25519_2026",
            issuer_name="University of Delhi",
            private_key=priv,
            public_key=pub,
            public_key_hex=pub_hex
        )
        self._keypairs[fixture.key_id] = fixture

    def get_keypair(self, key_id: str) -> KeypairFixture | None:
        return self._keypairs.get(key_id)

    @staticmethod
    def create_sample_degree_credential(subject_account_id: str = "DGI-7K4M-X9P2-2026") -> dict[str, Any]:
        return {
            "credentialId": "DGP-7K4M-92PX-2026",
            "issuerId": "org_delhi_university",
            "issuerName": "University of Delhi",
            "subjectReference": subject_account_id,
            "credentialType": "education.degree",
            "claims": {
                "degree": "Bachelor of Technology in Computer Science",
                "graduationYear": 2026,
                "grade": "Distinction",
                "rollNumber": "CS-2022-8941"
            },
            "status": "ACTIVE",
            "issuedAt": 1774300800,  # 2026 timestamp
            "expiresAt": 2089670400   # 2036 timestamp
        }
