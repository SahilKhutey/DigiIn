# DigiIn — Flagship Public-Service Journey: Scholarship Application

## 1. Journey Overview: Higher Education Scholarship Verification

The flagship demonstration journey follows **Rahul Sharma**, a college applicant using DigiIn to apply for the **National Merit-cum-Means Scholarship** at the **University of Delhi**.

Instead of a 45-minute multi-document upload ordeal, Rahul completes the application in **2 minutes** through a 6-step progressive disclosure flow:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE 6-STEP PROGRESSIVE DISCLOSURE                      │
│                                                                             │
│  [Step 1] Select Public Service (Scholarship Application - DU)             │
│     │                                                                       │
│  [Step 2] Review Required Credentials (Identity, Domicile, Income, Marks)  │
│     │                                                                       │
│  [Step 3] Automated Discovery of Pre-Verified Claims in Citizen Wallet     │
│     │                                                                       │
│  [Step 4] SIGNATURE SHARING REVIEW (What is Shared vs What is NOT Shared)   │
│     │                                                                       │
│  [Step 5] Purpose-Bound Consent Approval & Ed25519 Proof Minting            │
│     │                                                                       │
│  [Step 6] Instant Submission & Institutional 1-Click Cryptographic Verify  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Signature Screen: "Sharing Review"

The **Sharing Review Screen** is DigiIn's central trust artifact. It visually reassures the citizen that their privacy is strictly protected by explicitly enumerating disclosed predicates alongside strictly withheld personal data:

```
┌─────────────────────────────────────────────────────────────────┐
│  SCHOLARSHIP APPLICATION — UNIVERSITY OF DELHI                  │
│                                                                 │
│  The National Scholarship Board is requesting verification to   │
│  confirm your eligibility for the 2026 Merit Program.           │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  SHARED WITH INSTITUTION:                                       │
│  ✓ Full Name: Rahul Sharma                                      │
│  ✓ State Domicile: Chhattisgarh (Verified)                      │
│  ✓ Income Bracket: Below INR 2.5 Lakh / Year (Eligible)         │
│  ✓ Higher Secondary Status: Class XII Passed (94.2% Marks)      │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  NOT SHARED (KEPT PRIVATE IN YOUR VAULT):                       │
│  • Aadhaar Number (Redacted)                                    │
│  • Exact Salary / Tax Return Figures                            │
│  • Raw PDF Marksheet & Certificate Files                        │
│  • Full Residential Address & Family Details                    │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  PURPOSE: Scholarship Eligibility Determination                 │
│  VALIDITY: 24 Hours (Single-Use Audience Constraint)            │
│                                                                 │
│  [ ALLOW & SUBMIT APPLICATION ]         [ DECLINE REQUEST ]     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. The Institutional Perspective

When the university scholarship officer opens the application in the **Requester Console**, they receive a clean, verifiable decision card:

```
┌─────────────────────────────────────────────────────────────────┐
│  APPLICANT: RAHUL SHARMA (App #DU-SCH-2026-9912)                │
│  STATUS: VERIFIED ELIGIBLE ✓                                    │
│                                                                 │
│  VERIFIED CRITERIA:                                             │
│  • Identity Assertion:      ✓ Verified (DigiIn Sovereign Trust) │
│  • State Domicile:          ✓ Chhattisgarh Resident             │
│  • Income Requirement:      ✓ Eligible (< 2.5L Threshold)       │
│  • Academic Qualification:   ✓ CBSE Class XII (Score: 94.2%)    │
│                                                                 │
│  CRYPTOGRAPHIC EVIDENCE:                                        │
│  • Proof ID:        prf_sch_du_7788                             │
│  • Signature:       Valid Ed25519 (RFC 8785 Canonicalized)      │
│  • Issuer Trust:    DigiIn Root Trust Infrastructure (Trusted)  │
│  • Raw Files Held:  0 Bytes (Zero Storage Liability)           │
│                                                                 │
│  [ VIEW FULL CRYPTOGRAPHIC DETAILS ]     [ APPROVE SCHOLARSHIP ]│
└─────────────────────────────────────────────────────────────────┘
```
