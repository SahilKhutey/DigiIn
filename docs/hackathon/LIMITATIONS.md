# DigiIn — Known Limitations & Future Roadmap

## 1. Honest Scope & Current Prototype Boundaries

In keeping with the Builder Brief's emphasis on transparency, the following section outlines the explicit technical boundaries of this release candidate:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PROTOTYPE STATUS MATRIX                               │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ WHAT IS FULLY IMPLEMENTED & PROVEN   │ WHAT IS MOCKED / SIMULATED IN DEMO   │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ • Ed25519 asymmetric cryptography   │ • External state board network calls │
│ • RFC 8785 JSON canonicalization     │   (uses isolated adapter contracts)  │
│ • AES-256-GCM envelope encryption   │ • SMS / WhatsApp OTP gateways        │
│ • SHA-256 tamper-evident hash chain  │   (uses deterministic sandbox codes) │
│ • 43-suite automated test matrix     │ • Hardware HSM key storage           │
│ • 7-screen citizen scholarship flow  │   (uses local software key store)    │
│ • Signature Sharing Review generator │ • Live UIDAI eKYC API                │
│ • Data Saver compression engine      │   (uses synthetic demographic mocks) │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 2. Why Simulation is the Right Engineering Choice for Hackathons
1. **Security & Privacy**: Connecting real government identities or live UIDAI credentials during a hackathon introduces massive legal and security liabilities.
2. **Reliability & Determinism**: Simulated adapter contracts guarantee $100\%$ reproducible test execution, unaffected by external government downtime or rate limits.
3. **Decoupled Architecture**: DigiIn's adapter layer is designed such that swapping a mock adapter for a real government API requires zero changes to the core verification or consent engines.

---

## 3. Future Engineering Roadmap
1. **Hardware Security Module (HSM) Integration**: Support PKCS#11 and AWS CloudHSM for sovereign root key signing.
2. **Zero-Knowledge Succinct Proofs (zk-SNARKs)**: Upgrade from boolean predicate evaluations to full cryptographic zero-knowledge range proofs for income and age thresholds.
3. **Multi-Region Distributed Ledgers**: Shard the SHA-256 audit ledger across sovereign state nodes for cross-state federation.
