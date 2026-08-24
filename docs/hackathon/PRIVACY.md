# DigiIn — Privacy & Data Minimization Architecture

## 1. The Core Privacy Principle: Minimal Selective Disclosure

Under India's **Digital Personal Data Protection (DPDP) Act 2023**, personal data collection must be limited strictly to what is necessary for the specified purpose. DigiIn implements this principle natively at the protocol level:

```
                            WHAT THE INSTITUTION NEEDS
                                        │
                            "Is income < INR 2.5L?"
                                        │
                                        ▼
    TRADITIONAL APPROACH (LEAKY)               DIGIIN APPROACH (MINIMAL)
   ──────────────────────────────             ──────────────────────────
   • Full 3-page Form 16 PDF                  • {"income_eligible": true}
   • PAN Number & Aadhaar Number              • Zero PDF files transferred
   • Employer Name & Address                  • Single-use audience constraint
   • Bank Account Statements                  • 24-hour expiration
   ──────────────────────────────             ──────────────────────────
```

---

## 2. Privacy Enforcements in DigiIn

### A. The Signature "Sharing Review" Gate
- Before any proof is minted, the citizen is presented with an explicit breakdown of:
  - **What is shared**: Minimal predicates required by the service.
  - **What is withheld**: Original document files (0 bytes transferred), raw Aadhaar numbers, tax return PDFs, and full residential addresses.

### B. Automated PII Detection & Scrubbing
- The `PIIDetector` engine automatically scans all outbound payloads and structured audit logs.
- Sensitive regular expression patterns (Aadhaar 12-digit numbers, PAN formats, OTP codes, private keys) are intercepted and redacted before touching log files or wire protocols.

### C. Sovereign Consent Revocation
- Citizens can view all active sharing grants in their **Sharing Activity** view and revoke access with a single click, instantly rendering the proof token invalid for future queries.
