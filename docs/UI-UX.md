# DigiLocker X — UI/UX & Screen Specification

This document provides the authoritative screen layouts, information architecture, UI state system, accessibility requirements, and implementation contracts for all DigiLocker X interfaces.

---

## 1. Information Architecture & Route Map

```
/
├── / (Landing Page)
├── /login
├── /register
├── /dashboard
│
├── /documents
│   ├── / (Document Wallet)
│   ├── /search (Issuer Catalog Discovery)
│   ├── /upload (Upload & OCR Pipeline)
│   └── /[id] (Document Detail & Version History)
│
├── /credentials
│   ├── / (Verifiable Credential Store)
│   └── /[id] (Credential Claims & Trust Badges)
│
├── /verification
│   ├── / (Verification Dashboard)
│   ├── /requests (Pending Inbound Inquiries)
│   ├── /requests/[id] (Consent Review Modal)
│   └── /result/[id] (Cryptographic Proof Receipt)
│
├── /share
│   ├── / (Active Sharing Grants)
│   └── /[id] (Selective Disclosure Configurator)
│
├── /activity (Immutable Sovereign Audit Log)
├── /notifications (Transactional Alerts)
├── /corrections (Discrepancy Reporting)
├── /support (Diagnostic Support Sheets)
└── /settings (Passkeys, Devices, Language)
```

---

## 2. Universal UI State System

Every component and screen in the platform must explicitly handle all **8 UI States**. Never build only the happy path:

1. `LOADING`: Accessible skeleton loader with screen-reader announcement.
2. `EMPTY`: Informative empty state with a clear primary call-to-action.
3. `SUCCESS`: Validated data rendering with clear trust badges.
4. `ERROR`: Actionable error state with error code, recovery suggestion, and retry button.
5. `PENDING`: Real-time status indicator showing asynchronous progress.
6. `OFFLINE`: Graceful offline cache display with clear warning banner.
7. `UNAUTHORIZED`: Permission prompt redirecting to authenticated elevation flow.
8. `EXPIRED`: Session or token expiration state with one-click re-authentication.

---

## 3. Screen Specifications & Wireframes

### Screen 01: Landing Page (`/`)
```
┌─────────────────────────────────────────────────────────────┐
│ DigiLocker X                           [ Login ] [ Register ]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Your documents. Your verification. Your control.           │
│                                                             │
│  Verify government credentials without repeatedly           │
│  uploading physical files.                                  │
│                                                             │
│  [ Get Started ]      [ How Verification Works ]            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  ✓ Government-issued credentials (CBSE, UIDAI, MoRTH)       │
│  ✓ Zero-knowledge minimum disclosure proofs                 │
│  ✓ Explicit, revocable citizen consent                      │
│  ✓ Full parity on Web & Mobile (WCAG 2.2 AA)                │
└─────────────────────────────────────────────────────────────┘
```

### Screen 02: Login / OTP (`/login`)
```
┌─────────────────────────────────────────────────────────────┐
│                        Sign in                              │
│                                                             │
│ Mobile number                                               │
│ [ +91 98765 43210                                         ] │
│                                                             │
│ [ Send OTP ]                                                │
│                                                             │
│ ───────────────────────── or ────────────────────────────── │
│                                                             │
│ [ Continue with Passkey / Biometrics ]                      │
│                                                             │
│ Need help signing in? • Terms of Public Service             │
└─────────────────────────────────────────────────────────────┘
```

### Screen 03: Citizen Dashboard (`/dashboard`)
```
┌─────────────────────────────────────────────────────────────┐
│ Good afternoon, Rahul Sharma              [ 🔔 2 ] [ Rahul ]│
├─────────────────────────────────────────────────────────────┤
│ What do you need to do?                                     │
│                                                             │
│ [ + Get Document ]  [ 🔍 Verify ]  [ 📤 Share ]  [ 📁 Upload ]│
├─────────────────────────────────────────────────────────────┤
│ Verifiable Credentials                                      │
│                                                             │
│ ✓ Class XII Certificate     CBSE               Level 4 Verified
│ ✓ Aadhaar Demographic       UIDAI              Level 4 Verified
│ ⏳ B.Tech Degree             State University   Pending Review │
├─────────────────────────────────────────────────────────────┤
│ Pending Consent Requests                                    │
│                                                             │
│ ⚠️ National Testing Agency wants Class XII verification      │
│ [ Review & Decide ]                                         │
└─────────────────────────────────────────────────────────────┘
```

### Screen 04: Document Wallet (`/documents`)
```
┌─────────────────────────────────────────────────────────────┐
│ Documents & Credentials                                     │
│ [ Search documents...                                     ] │
│                                                             │
│ Filter: [ All ] [ Education ] [ Identity ] [ Transport ]    │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Class XII Passing Certificate                           │ │
│ │ Issuer: Central Board of Secondary Education (CBSE)     │ │
│ │ Status: ✓ Level 4 Verified (Direct Government Issuer)   │ │
│ │ Issued: 15 May 2026 • Passing Year: 2026                │ │
│ │                                                         │ │
│ │ [ View Details ]   [ Create Proof ]   [ Share Claim ]   │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Screen 05: Document Detail (`/documents/[id]`)
```
┌─────────────────────────────────────────────────────────────┐
│ Class XII Passing Certificate             [ ← Back to Wallet]│
├─────────────────────────────────────────────────────────────┤
│ ✓ Government Verified Claim (CBSE)                          │
│                                                             │
│ Issuer: Central Board of Secondary Education                │
│ Verification Level: Level 4 (Cryptographic Registry Match)  │
│ Issued: 15 May 2026                                         │
│ Status: ACTIVE                                              │
│ SHA-256 Hash: 8f9a2b...4d5e                                 │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│ Actions:                                                    │
│ [ Generate Proof Token ]  [ Share Credential ]  [ Report Fix ]│
└─────────────────────────────────────────────────────────────┘
```

### Screen 06: Verification Consent Request Modal (`/verification/requests/[id]`)
```
┌─────────────────────────────────────────────────────────────┐
│ 🛡️ Verification Request                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ National Testing Agency (NTA) requests verification of your │
│ Class XII Qualification.                                    │
│                                                             │
│ Requested Attributes:                                       │
│   ☑ Qualification (Senior School Certificate Examination)   │
│   ☑ Passing Year (2026)                                     │
│   ☐ Full Marks Breakdown (Not required - unchecked)         │
│                                                             │
│ Purpose: Joint Entrance Examination (JEE) Application       │
│ Validity: Single-use (Expires in 15 minutes)                │
│                                                             │
│ ℹ️ Your original document PDF is NEVER downloaded.          │
│ Only the cryptographic verification result is shared.       │
│                                                             │
│ [ Decline Request ]              [ Allow Verification Proof ]│
└─────────────────────────────────────────────────────────────┘
```

### Screen 07: Verification Result & Proof Receipt (`/verification/result/[id]`)
```
┌─────────────────────────────────────────────────────────────┐
│ 🛡️ Verification Complete                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                     ✓ VERIFIED                              │
│                                                             │
│ Claim: Class XII Qualification                              │
│ Issuer: CBSE (Level 4 Sovereign Authority)                  │
│ Passing Year: 2026                                          │
│ Shared With: National Testing Agency                        │
│ Proof Token: eyJhbGciOiJFZERTQSI...8f9a                     │
│ Timestamp: 22 Aug 2026, 14:15 IST                           │
│                                                             │
│ [ Download Proof Receipt ]                       [ Done ]   │
└─────────────────────────────────────────────────────────────┘
```

### Screen 08: Mobile App 5-Tab Navigation Layout
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                       Mobile Viewport                       │
│                                                             │
│               [ Active Screen / Wallet / Verify ]           │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│   [🏠 Home]  [👝 Wallet]  [🛡️ Verify]  [📋 Activity]  [👤 Me]│
└─────────────────────────────────────────────────────────────┘
```

### Screen 09: Issuer Console (`/issuer`)
```
┌─────────────────────────────────────────────────────────────┐
│ CBSE — Issuer Administration Dashboard                      │
├─────────────────────────────────────────────────────────────┤
│ Total Issued: 1,284,912  •  Verified Queries: 1,241,008      │
│ Pending Review: 3,204    •  Revoked: 12,300                 │
├─────────────────────────────────────────────────────────────┤
│ Inbound Verification Queue                                  │
│ [ Search roll numbers / students...                       ] │
│ [ Issue Single Credential ]      [ Batch Bulk Upload (CSV) ] │
└─────────────────────────────────────────────────────────────┘
```

### Screen 10: Government Officer Queue (`/officer`)
```
┌─────────────────────────────────────────────────────────────┐
│ Discrepancy Queue: CASE-92831 (Class XII Match)             │
├─────────────────────────────────────────────────────────────┤
│ Citizen: Protected Identity (subj_demo_5c7b90)              │
│ Claimed Issuer: Central Board of Secondary Education        │
│ Automated Match Score: 78% (Name spelling slight variance)  │
│                                                             │
│ Uploaded Evidence OCR         Registry Authoritative Record │
│ Name: RAHUL SHARMA            Name: RAHUL SHARMA            │
│ Roll No: 26182910             Roll No: 26182910             │
│ Year: 2026                    Year: 2026                    │
│                                                             │
│ [ ✓ Approve ]  [ ✕ Reject ]  [ 💬 Clarify ]  [ ↗ Escalate ] │
└─────────────────────────────────────────────────────────────┘
```

### Screen 11: Requester Portal (`/verifier`)
```
┌─────────────────────────────────────────────────────────────┐
│ Requester Portal — National Testing Agency                  │
├─────────────────────────────────────────────────────────────┤
│ Create New Verification Request                             │
│                                                             │
│ Required Credential: [ Class XII Passing Certificate      ▼ ]│
│ Purpose:             [ Examination Admission Eligibility  ▼ ]│
│ Attributes:          ☑ Qualification  ☑ Passing Year         │
│ Min Level:           [ Level 4 - Government Authority     ▼ ]│
│                                                             │
│ [ Create & Dispatch Verification Request ]                  │
└─────────────────────────────────────────────────────────────┘
```

### Screen 12: Admin System Governance (`/admin`)
```
┌─────────────────────────────────────────────────────────────┐
│ DigiLocker X — System Administration                        │
├─────────────────────────────────────────────────────────────┤
│ [ Users ] [ Organizations ] [ Issuers ] [ Policies ] [ Audit]│
│                                                             │
│ System Health: 100% Operational • HSM Status: ACTIVE        │
│ Active Issuers: 42 Boards • Verification Throughput: 450/sec│
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Accessibility Specification (WCAG 2.2 AA)

1. **Focus Rings & Keyboard Trap Prevention**: Visible 2px focus indicators on interactive elements (`outline: 2px solid #2563eb`).
2. **Screen Reader Compliance**: `aria-live="polite"` on status updates and state changes; all icon buttons equipped with `aria-label`.
3. **Contrast Ratios**: Normal text >= 4.5:1, large text and essential UI badges >= 3.0:1.
4. **Multilingual Internationalization**: RTL/LTR flexibility, Unicode Hindi UTF-8 string localization dictionary ready.
