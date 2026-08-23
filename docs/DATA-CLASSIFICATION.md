# DigiIn Data Classification & Privacy Minimization Policy

## 1. Data Classification Taxonomy

| Tier | Category | Examples | Storage & Encryption Controls |
| :--- | :--- | :--- | :--- |
| **Tier 1** | `PUBLIC` | Platform version, public status, provider capabilities, proof verification schema | Plaintext / CDN Cached |
| **Tier 2** | `INTERNAL` | Organisation names, rate limit metrics, operational logs | Database / TLS 1.3 in Transit |
| **Tier 3** | `SENSITIVE` | User email, phone hash, session metadata, consent records | Database AES-256 / Masked Logs |
| **Tier 4** | `HIGHLY_SENSITIVE` | Raw document PDFs, identity attributes, biometric/OCR evidence, private signing keys | AES-256-GCM at Rest / Private Object Storage / Ephemeral Memory |

---

## 2. Privacy & Minimization Principles

1. **Selective Claim Disclosure**: Organisations verify assertions (e.g. `EDUCATION_VERIFIED: Qualification >= 60%`) without accessing raw certificate PDFs or residential addresses.
2. **Zero PII in Logs**: Audit events record resource IDs, action codes, and timestamps; raw citizen certificates and plaintext passwords are never logged.
3. **Short-Lived Signed Tokens**: Direct access to document binaries in private object storage requires short-lived (300s) HMAC-signed authorization tokens.
4. **Instant Citizen Revocation**: Citizens retain the unilateral right to revoke active consents and active sharing proofs at any time.
