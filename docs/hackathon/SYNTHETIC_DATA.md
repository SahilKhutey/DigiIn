# DigiIn — Synthetic Data Boundaries & Sandbox Fixtures

## 1. Strict Synthetic Data Policy

In full compliance with the hackathon builder guidelines and privacy ethics, **DigiLocker X (DigiIn) uses 100% synthetic, mocked, and generated test fixtures**:

```
                       SYNTHETIC DATA ISOLATION BOUNDARY
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                              ▼
  ZERO REAL AADHAAR              ZERO REAL PAN                  ZERO REAL OTPs
  (Mocked DIN-DEMO-001)          (Mocked Alpha Patterns)        (Deterministic Sandbox)
        │                              │                              │
        └──────────────────────────────┼──────────────────────────────┘
                                       ▼
                     ZERO LIVE GOVERNMENT API INTEGRATION
```

---

## 2. Pre-Seeded Demonstration Fixtures

| Persona / Entity | Identifier | Organization | Purpose |
|---|---|---|---|
| **Demo Citizen** | `DIN-DEMO-001` | Sovereign Citizen Holder | Applicant applying for merit scholarship |
| **Demo Institution** | `ORG-DEMO-001` | University Scholarship Service | Relying party verifying applicant eligibility |
| **Demo Issuer** | `ISSUER-DEMO-001` | DigiIn Verified Demo Authority | Root trust anchor signing credential proofs |
| **Valid Proof** | `PRF-DEMO-1042` | University of Delhi Scholarship | Authentic baseline proof for live demo |
| **Tampered Proof** | `PRF-TAMPERED-01` | Verification Lab Test | Injected altered score predicate |
| **Expired Proof** | `PRF-EXPIRED-01` | Verification Lab Test | Stale timestamp past 24h validity |
| **Revoked Proof** | `PRF-REVOKED-01` | Verification Lab Test | Revoked status in certificate revocation list |

---

## 3. Official Disclaimer

> **IMPORTANT DISCLAIMER**: DigiLocker X (DigiIn) is an independent engineering prototype developed for the *Build What Moves India* hackathon. It is **not** an official government service and does **not** connect to live production government infrastructure, UIDAI, or CBDT databases. All citizen names, identifiers, and certificates are strictly fictional.
