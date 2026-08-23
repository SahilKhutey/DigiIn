# DigiIn Production Security Architecture & Policies

## 1. Core Security Principles

1. **Zero Trust & Explicit Verification**: No request or service is trusted implicitly. Every action is authenticated, authorized, and verified against tenant and resource boundaries.
2. **Data Minimization & Selective Disclosure**: DigiIn stores only necessary metadata and issues cryptographically signed claims (`EDUCATION_VERIFIED`) rather than disclosing raw personal documents.
3. **Defense in Depth**: Security controls are enforced in layers (WAF $\rightarrow$ API Gateway $\rightarrow$ Role Authorization $\rightarrow$ Resource Ownership Guard $\rightarrow$ Data Encryption at Rest).
4. **Key Separation & Isolation**: Separate cryptographic keys are used for session tokens, API keys, webhook signatures, document storage encryption, and proof minting.
5. **No Secrets in Source**: No credentials, API tokens, or encryption keys are committed to Git, embedded in client builds, or logged to disk.

---

## 2. Cryptographic Standards

- **Password Hashing**: PBKDF2-HMAC-SHA256 (100,000 rounds) / Argon2id with 128-bit random salt.
- **Proof Signing**: Asymmetric Ed25519 (EdDSA) with canonical RFC 8785 JSON payloads.
- **Document Integrity**: SHA-256 binary hash digest generated upon file receipt.
- **Token Encryption**: AES-256-GCM for external provider OAuth access/refresh tokens.
- **Webhook Signatures**: HMAC-SHA256 with timing-safe comparison.

---

## 3. Rate Limiting & Abuse Prevention

Tiered token bucket rate limiters prevent denial-of-service and credential stuffing:
- **Login**: 5 requests / minute
- **OTP Challenge**: 3 requests / minute
- **Document Upload**: 10 uploads / minute
- **Verification Job**: 30 requests / minute
- **Public Proof Validation**: 120 requests / minute
- **Health Probes**: 300 requests / minute
- **Admin APIs**: 20 requests / minute

---

## 4. Secure Development Lifecycle (SDLC)

- All pull requests pass static analysis (Ruff / ESLint), type checking (`tsc`), dependency scanning, unit/integration security tests, and E2E regression pipelines prior to merge.
