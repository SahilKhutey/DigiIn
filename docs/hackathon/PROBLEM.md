# DigiIn — Problem Statement & Public-Service Inefficiency

## 1. The Core Problem

In Indian public services today, citizens repeatedly submit the same identity, educational, and income documents to different public and institutional portals, even when those exact facts have already been authoritatively verified by sovereign authorities.

```
                               THE BROKEN REALITY
                       (Redundant, Painful & Insecure)

                            CITIZEN (Applicant)
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
    Service A                   Service B                   Service C
(College Admission)        (State Scholarship)         (Tuition Fee Waiver)
         │                           │                           │
  ├── Upload Aadhaar          ├── Upload Aadhaar          ├── Upload Aadhaar
  ├── Upload 12th Marksheet   ├── Upload 12th Marksheet   ├── Upload 12th Marksheet
  ├── Upload Income Cert      ├── Upload Income Cert      ├── Upload Income Cert
  ├── Upload Domicile Cert    ├── Upload Domicile Cert    ├── Upload Domicile Cert
  └── Wait 3-4 Weeks          └── Wait 4-6 Weeks          └── Wait 3-4 Weeks
```

---

## 2. Why the Existing System is Broken

1. **Repetitive Citizen Friction**:
   - Applying for four public schemes requires scanning, resizing, and uploading the same 4 physical documents 16 separate times.
   - Mobile users on slow 2G/3G connections frequently suffer failed uploads, session timeouts, and lost progress.

2. **Severe Privacy & Data Governance Liabilities**:
   - Centralized departmental databases store millions of raw unredacted PDF scans containing full Aadhaar numbers, parental tax returns, and home addresses.
   - Every department becomes an unnecessary data honeypot vulnerable to breaches.

3. **Massive Institutional Verification Backlog**:
   - Institutional officers spend hundreds of thousands of hours manually squinting at watermarks and blurred scans to detect forged documents.
   - Legitimate applicants wait weeks for approvals that should take seconds.

---

## 3. The DigiIn Paradigm: Verify Once, Reuse Everywhere

DigiIn replaces raw document file transfers with **cryptographically verifiable, purpose-bound claims**:

$$\text{Verify Fact Once} \longrightarrow \text{Store Sovereign Credential} \longrightarrow \text{Citizen Selects What to Share} \longrightarrow \text{Service Receives Proof}$$

- **Zero Document Uploads**: The citizen shares cryptographic proofs, not multi-megabyte PDF copies.
- **Zero Raw PII Leaks**: The relying party receives answers to questions (*"Is income $< 2.5\text{L}$?"*), not raw tax forms.
- **Instant Mathematical Verification**: Verification takes under 5 milliseconds using asymmetric Ed25519 signatures.
