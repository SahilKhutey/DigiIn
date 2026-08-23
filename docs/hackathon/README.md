# DigiIn — Hackathon Evidence & Verification Package

DigiIn is a user-controlled digital trust and verification layer that allows citizens to maintain cryptographically authentic credentials and verify them directly with external government departments, universities, employers, and financial services without repeatedly uploading copies of physical documents.

## 🏆 Key Differentiation: Verification vs Document Storage

1. **Not Document Storage**: DigiIn verifies credentials cryptographically; a document existing in storage does not make it verified.
2. **Explicit Citizen Consent**: Services request specific claims; the citizen reviews the purpose and grants explicit, time-bounded consent (`[Allow & Verify]`).
3. **Minimal Disclosure**: Services receive only verified Boolean/attribute claims (`education.degree: VERIFIED`), without leaking unrequested PII or raw PDFs.
4. **Institutional Review & Decision Separation**: DigiIn verifies cryptographic authenticity; the verifying institution independently reviews eligibility and records departmental decisions (`APPROVED` / `REJECTED`).

## 📚 Evidence Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md): Multi-tier system architecture and trust boundaries.
- [VERIFICATION.md](VERIFICATION.md): Cryptographic verification pipeline and negative test results.
- [SECURITY.md](SECURITY.md): Security controls, PBKDF2/Ed25519 cryptography, and IDOR protection.
- [THREAT-MODEL.md](THREAT-MODEL.md): STRIDE threat modeling and mitigations.
- [TEST-RESULTS.md](TEST-RESULTS.md): Monorepo test matrix across all 34 test suites.
- [API.md](API.md): Standardized REST API endpoints and error envelopes.
- [DEMO.md](DEMO.md): 5–7 minute dual-browser live demonstration script.
- [LIMITATIONS.md](LIMITATIONS.md): Clear statement of current MVP scope and production roadmap.
