# DigiIn — System Architecture

## 1. Public-Service-First Architecture

DigiIn's architecture reverses traditional infrastructure design: the system is structured around the **citizen's public-service journey**, with the cryptographic trust and verification mechanisms serving as an enabling foundation.

```
                              PUBLIC SERVICE
                           (Scholarship / Scheme)
                                     │
                                     ▼
                              DigiIn UX Layer
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
      Citizen                   Institution                    Issuer
(Wallet & Sharing)          (Verifier Query)             (Credential Mint)
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     ▼
                            Verification Layer
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
    Credentials                   Consent                      Proof
 (Authoritative Claims)    (Purpose-Bound Scopes)      (Ed25519 Signatures)
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     ▼
                              Trust & Security
              (Envelope Encryption • RFC 8785 • SHA-256 Hash Chain)
```

---

## 2. Core Architectural Subsystems

### A. Frontend Surfaces (`apps/`)
- **Citizen Web Portal (`apps/web`)**: Service-first single-page application built with React, Vite, and Tailwind CSS. Implements progressive disclosure, high-contrast accessible UI, and Data Saver mode.
- **Verifier Console (`apps/verifier-console`)**: Streamlined dashboard for university officers to inspect cryptographic proofs and verified predicates.
- **Admin Console (`apps/admin`)**: Operations and tamper-evident audit stream explorer.

### B. Core API & Domain Services (`services/api/`)
- **Public Service Subsystem (`app/core/public_service/`)**: Service registry, application state machine, signature Sharing Review generator, and low-bandwidth optimization engine.
- **Cryptographic Proof Subsystem (`app/core/proofs/`)**: Ed25519 asymmetric signing, RFC 8785 canonical JSON serialization, and Trust Registry verification.
- **Security & Privacy Subsystem (`app/core/security/`)**: AES-256-GCM envelope encryption, ABAC policy engine, SHA-256 tamper-evident linked audit ledger, and PII redaction filters.
- **Operations & Reliability Subsystem (`app/core/operations/`)**: Asynchronous priority job workers, DLQ, idempotency engine, 3-tier health probes, and disaster recovery coordinators.

---

## 3. Data Flow: Citizen Request to Institutional Proof

1. **Discovery**: Citizen requests application $\rightarrow$ System fetches encrypted credentials from vault.
2. **Minimization**: Policy engine extracts only requested boolean predicates (e.g. `income_eligible: true`).
3. **Canonicalization**: Claims are normalized via RFC 8785 JSON canonicalization.
4. **Signing**: Issuer / Node signs digest with private Ed25519 key.
5. **Verification**: Relying party validates signature using public JWKS trust anchors (`/.well-known/jwks.json`) in $< 5\text{ms}$.
