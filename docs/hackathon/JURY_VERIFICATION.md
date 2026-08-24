# DigiLocker X (DigiIn) — Jury & Judge Verification Guide

## 1. Quickstart: 1-Click Verification for Judges

Judges and evaluators can verify the entire platform, its security model, and cryptographic guarantees in seconds using the following pre-configured commands:

### A. Run Interactive Flagship Showcase
Executes the live 10-milestone demonstration across Citizen, Department, and Operator roles:
```powershell
python scripts/hackathon_showcase.py
```

### B. Run Complete Automated Test Matrix
Runs all automated unit, integration, security, and negative proof test suites:
```powershell
python tests/run_all_tests.py
```

### C. Verify Cryptographic Proofs Offline
Mathematically validates Ed25519 verifiable credentials offline without running the backend server:
```powershell
python tests/cli_proof_verifier.py --demo
```

---

## 2. Key Architectural Highlights to Evaluate

| Feature | What to Look For | Where to Inspect |
|---|---|---|
| **Zero Raw Document Transfer** | Verifiers receive boolean claims (`income_eligible: true`), never PDF binaries or raw Aadhaar numbers. | `docs/Principles.md`, `tests/test_phase36_verification_hardening.py` |
| **Negative Proof Defense** | Altering a single character in a signed proof causes instant cryptographic rejection. | `app/core/verification_hardening/negative_proof_engine.py` |
| **Tamper-Evident Audit Chain** | Every verification event is appended to a SHA-256 hash-linked chain with zero PII. | `app/core/security/audit_chain.py` |
| **Provider Isolation** | The core domain never directly calls department APIs; external providers are isolated behind adapters. | `app/integrations/` |
| **Operational Resilience** | If an external government API goes offline, existing credentials remain verifiable offline via cached trust anchors. | `app/core/operations/health_probes.py` |

---

## 3. Interactive Negative Proof Lab Guide

Judges can test malicious scenarios directly:

```
Scenario 1: Alter Claim Value
Action:     Attacker modifies score in token from "94.2%" to "100%".
Result:     REJECTED (Reason: DIGEST_INTEGRITY_CHECK failed)

Scenario 2: Rogue Issuer
Action:     Attacker issues credential using unauthorized DID "did:gov:fake-issuer".
Result:     REJECTED (Reason: ISSUER_TRUST_CHECK failed)

Scenario 3: Revoked Credential
Action:     Presenting a certificate revoked by the issuing authority.
Result:     REJECTED (Reason: REVOCATION_CHECK failed)

Scenario 4: Expired Proof
Action:     Presenting a verification token past its 15-minute validity window.
Result:     REJECTED (Reason: EXPIRATION_CHECK failed)
```

---

## 4. Evaluation Rubric Alignment

| Criteria | DigiLocker X Implementation | Evidence |
|---|---|---|
| **Technical Complexity** | Asymmetric Ed25519 proofs, RFC 8785 canonicalization, AES-256-GCM envelope encryption, ABAC engine, SHA-256 hash chains, background workers with DLQ. | 41 Test Suites (100% PASS), `app/core/` |
| **Privacy & Security by Design** | Strict purpose limitation, zero raw document transfers, zero PII logging, anti-replay nonces, rate limiting. | `docs/hackathon/EVIDENCE_MATRIX.md` |
| **Real-World Viability** | Standards-compliant JWKS discovery, multi-tier trust badges, WCAG 2.2 AA accessible UI, bilingual English/Hindi localization. | `apps/web`, `apps/issuer-console`, `apps/verifier-console` |
| **Completeness & Rigor** | 100% automated test coverage across 37 phases, versioned migrations, disaster recovery drills with RTO $\le 60$m. | `tests/run_all_tests.py` |
