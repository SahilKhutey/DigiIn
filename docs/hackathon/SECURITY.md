# DigiIn — Security Architecture & Cryptographic Threat Model

## 1. Zero-Trust Security Foundation

DigiIn enforces strict zero-trust security invariants across every credential, consent grant, proof verification, and audit record.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DIGIIN SECURITY ARCHITECTURE                          │
│                                                                             │
│  [Rest]      AES-256-GCM Envelope Encryption (Dynamic DEK per document)    │
│  [Transit]   TLS 1.3 + Strict Transport Security (HSTS) + CSP               │
│  [Proof]     Ed25519 Asymmetric Signatures + RFC 8785 Canonical JSON       │
│  [Access]    Attribute-Based Access Control (ABAC Policy Engine)            │
│  [Audit]     SHA-256 Immutable Linked Hash Chain (H_n = Hash(E_n || H_n-1)) │
│  [Replay]    Single-Use Anti-Replay Nonce Tracking + 15m Expiration Window  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Threat Model & Defense Mechanisms

| Threat Scenario | Attacker Objective | DigiIn Defense Mechanism | Verification Outcome |
|---|---|---|---|
| **Claim Tampering** | Attacker alters marksheet score in token from 94% to 100%. | RFC 8785 Canonical JSON digest recalculation detects signature mismatch. | **`INVALID ✗`** (`DIGEST_INTEGRITY_CHECK`) |
| **Rogue Issuer** | Attacker creates forged credential with fake issuer DID. | Trust Registry verifies issuer against accredited Root anchors. | **`UNTRUSTED ✗`** (`ISSUER_TRUST_CHECK`) |
| **Replay Attack** | Intercepted proof token is reused for another service. | Audience restriction (`aud`) and single-use anti-replay nonce tracking. | **`REJECTED ✗`** (`NONCE_REPLAY_CHECK`) |
| **Stale / Revoked Proof** | Citizen presents certificate revoked by state board. | Real-time status lookup rejects suspended credentials. | **`REVOKED ✗`** (`REVOCATION_CHECK`) |
| **Expired Proof** | Presenting proof past its validity TTL. | Timestamp evaluation rejects tokens beyond validity window. | **`EXPIRED ✗`** (`EXPIRATION_CHECK`) |
| **Audit Ledger Tampering** | Malicious admin attempts to alter past access logs. | SHA-256 linked hash chain breaks immediately if any event is edited. | **`TAMPER_DETECTED ✗`** |

---

## 3. Cryptographic Standards Compliance
- **RFC 8785**: JSON Canonicalization Scheme (JCS) ensuring cross-platform bit-level deterministic digests.
- **RFC 8032**: Edwards-curve Digital Signature Algorithm (Ed25519) providing high performance and 128-bit post-quantum security margin.
- **RFC 7517**: JSON Web Key Set (JWKS) discovery format (`/.well-known/jwks.json`) for seamless offline third-party validation.
