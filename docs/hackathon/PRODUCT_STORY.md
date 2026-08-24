# DigiIn — Product Story & Problem Statement

## 1. The Real Citizen Problem: "Stop Submitting the Same Documents Again and Again"

In Indian public services today, citizens repeatedly navigate cumbersome application processes where every department acts as an isolated silo. A student applying for a university admission, a state scholarship, and a fee waiver is forced to upload the exact same physical scans and PDFs to three different portals:

```
                               THE TRADITIONAL PAIN
                       (Fragmented, Redundant & Leaky)

                            CITIZEN (Rahul Sharma)
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
   Department A                  Department B                  Department C
(College Admission)         (National Scholarship)         (State Fee Waiver)
         │                             │                             │
   ├── Upload Aadhaar            ├── Upload Aadhaar            ├── Upload Aadhaar
   ├── Upload 10th/12th PDF      ├── Upload 10th/12th PDF      ├── Upload 10th/12th PDF
   ├── Upload Income Cert        ├── Upload Income Cert        ├── Upload Income Cert
   ├── Upload Domicile Cert      ├── Upload Domicile Cert      ├── Upload Domicile Cert
   └── Wait 3-4 Weeks            └── Wait 4-6 Weeks            └── Wait 3-4 Weeks
```

### The Unintended Consequences:
1. **Massive Cognitive Load**: Citizens spend hours scanning, resizing, and re-entering identical information.
2. **Severe Privacy Risks**: Centralized departmental databases become honeypots storing millions of unredacted Aadhaar scans, tax forms, and residential documents.
3. **Heavy Administrative Burden**: Government officers spend months manually verifying scanned watermarks and signatures.

---

## 2. The DigiIn Solution: One Simple Experience Powered by Reusable Verification

DigiIn transforms this broken paradigm. A citizen verifies their information once; from that moment on, they simply authorize purpose-bound, minimal cryptographic proofs to relying services in seconds:

```
                               THE DIGIIN EXPERIENCE
                       (Fast, Sovereign & Zero Raw Transfers)

                            CITIZEN (Rahul Sharma)
                                       │
                                       ▼
                             DigiIn Sovereign Node
                          (Verified Claims at Rest)
                                       │
                                       ▼
                       Choose Service: Scholarship Portal
                                       │
                                       ▼
                         "Use My Verified Information"
                                       │
                                       ▼
                       Review Sharing (Zero Raw Files)
                                       │
                                       ▼
                       One-Click Purpose-Bound Consent
                                       │
                                       ▼
                             Application Submitted
                                   (2 Minutes)
                                       │
                                       ▼
                           University / Institution
                       (Instantly Verified Proof ✓)
```

---

## 3. Product Principles

1. **You Shouldn't Have to Prove the Same Thing Five Times**: If a claim (e.g. CBSE 12th marksheet, state domicile) has already been authoritatively verified, the citizen should be able to reuse that verified status instantly.
2. **Verify, Don't Copy**: Relying institutions need answers to questions (*"Is Rahul eligible for this scholarship?"*), not copies of raw PDF files or Aadhaar numbers.
3. **Minimal Selective Disclosure**: Disclose only the exact predicate required by the service (e.g., `income_eligible: true`), withholding all unneeded personal data.
4. **Service-First Simplicity**: Citizens do not log in to manage complex cryptographic engines; they log in to get a public service completed quickly and securely.
