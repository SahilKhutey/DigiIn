# DigiIn — Comprehensive Operational Flowcharts

This document compiles the 10 core operational sequence and workflow flowcharts across the platform.

---

## 📌 Flow 1: Sovereign Citizen Identity & Account Creation

```mermaid
sequenceDiagram
    autonumber
    actor Citizen as Citizen / User
    participant Web as DigiIn Web App
    participant API as DigiIn Gateway API
    participant Auth as PBKDF2 / Argon2id Auth Engine
    participant DB as Account & State Store

    Citizen->>Web: Register (Email, Mobile, Password)
    Web->>API: POST /v1/auth/register
    API->>Auth: Hash Password with Salt & PBKDF2
    API->>API: Generate Opaque Account ID (DGI-XXXX-XXXX-XXXX)
    API->>DB: Persist Citizen Account & Security State
    API-->>Web: Return Registration Success & Session Token
    Web-->>Citizen: Display Sovereign DigiIn Account Dashboard
```

---

## 📌 Flow 2: Issuer Credential Issuance & Signing

```mermaid
sequenceDiagram
    autonumber
    actor Issuer as University / Board Issuer
    participant API as DigiIn Issuer API
    participant Crypto as Ed25519 Cryptographic Engine
    participant Reg as National Trust Registry
    participant DB as Credential Registry

    Issuer->>API: POST /v1/products (Subject Reference, Claims)
    API->>Reg: Verify Issuer Accreditation (A1-A4 Level)
    API->>Crypto: RFC 8785 JSON Canonicalization
    Crypto->>Crypto: Compute SHA-256 Digest
    Crypto->>Crypto: Sign with Issuer Ed25519 Private Key
    API->>DB: Store Signed Credential (Status: ACTIVE)
    API-->>Issuer: Return Product ID (DGP-XXXX-XXXX-XXXX)
```

---

## 📌 Flow 3: Institutional Request & Purpose-Bound Citizen Consent

```mermaid
sequenceDiagram
    autonumber
    actor Verifier as Scholarship Portal
    participant API as DigiIn Verification API
    participant Inbox as Citizen Inbox (/requests)
    actor Citizen as Citizen
    participant Engine as Verification Coordinator

    Verifier->>API: POST /v1/verification-requests (DGI-ID, Purpose, Claims)
    API->>Inbox: Register Request (Status: DELIVERED)
    Inbox-->>Citizen: Emit In-App & Push Notification
    Citizen->>Inbox: Open & View Request Details (/requests/:id)
    Inbox->>API: Transition State -> VIEWED
    Citizen->>Inbox: Click [Allow & Verify]
    Inbox->>Engine: Create Purpose-Bound Consent Record (Status: ACTIVE)
    Engine->>Engine: Initiate Authoritative Verification
```

---

## 📌 Flow 4: Product Verification Engine (7-Point Check Matrix)

```mermaid
flowchart TD
    Req[Verification Request Ingress] --> C1{1. Product Exists?}
    C1 -- No --> F1[Outcome: UNKNOWN - Not Found]
    C1 -- Yes --> C2{2. Issuer in Trust Registry?}
    C2 -- No --> F2[Outcome: UNTRUSTED - Issuer Unaccredited]
    C2 -- Yes --> C3{3. Ed25519 Signature Valid?}
    C3 -- No --> F3[Outcome: INVALID - Forged Signature]
    C3 -- Yes --> C4{4. SHA-256 Digest Intact?}
    C4 -- No --> F4[Outcome: INVALID - Tampered Claims]
    C4 -- Yes --> C5{5. Validity Not Expired?}
    C5 -- No --> F5[Outcome: EXPIRED - Validity Ended]
    C5 -- Yes --> C6{6. Not Revoked / Suspended?}
    C6 -- Revoked --> F6[Outcome: REVOKED - Authoritatively Revoked]
    C6 -- Suspended --> F7[Outcome: SUSPENDED - Temporary Hold]
    C6 -- Active --> C7{7. Policy & Purpose Satisfied?}
    C7 -- Yes --> Success[Outcome: VERIFIED with High Assurance]
```

---

## 📌 Flow 5: Minimal Disclosure & Selective Disclosure

```mermaid
sequenceDiagram
    autonumber
    participant Engine as Verification Engine
    participant Validator as Privacy Proof Validator
    participant Service as External Service Portal

    Engine->>Validator: Inspect Full Credential (Degree, RollNo, DOB, Grade)
    Validator->>Validator: Filter strictly to Consented Claims (Degree, Year)
    Validator->>Validator: Mask RollNo, DOB, Grade & Exclude Raw Binaries
    Validator-->>Service: Return { "education.degree": "VERIFIED", "education.graduationYear": "VERIFIED" }
```

---

## 📌 Flow 6: Embeddable Service Integration Widget Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Citizen / Applicant
    participant Portal as Partner Scholarship Portal
    participant Widget as DigiIn Widget ("Continue with DigiIn")
    participant DigiIn as DigiIn Authorization Server

    User->>Portal: Start Application
    Portal->>Widget: Render DigiIn Widget
    User->>Widget: Click "Continue with DigiIn"
    Widget->>DigiIn: Redirect /requests/auth?code=...
    DigiIn->>User: Display Purpose & Requested Claims
    User->>DigiIn: Click [Allow & Verify]
    DigiIn-->>Portal: Redirect with Auth Code
    Portal->>DigiIn: POST /v1/auth/token (Exchange Code for Claims)
    DigiIn-->>Portal: Deliver Minimal Verified Claims
```

---

## 📌 Flow 7: Departmental Stepper Wizard & Review Queue Decision

```mermaid
sequenceDiagram
    autonumber
    actor Reviewer as Admissions Officer
    participant Queue as Review Queue (/institution/review)
    participant Decision as Decision Engine
    participant Webhook as HMAC Webhook Dispatcher
    participant ERP as University ERP System

    Reviewer->>Queue: Open Verified Request
    Queue-->>Reviewer: Display DigiIn Cryptographic Verification (VERIFIED)
    Reviewer->>Decision: Submit Institutional Decision (APPROVED, Reason: Cutoff Met)
    Decision->>Decision: Record InstitutionalDecision Record
    Decision->>Webhook: Trigger institutional.decision.recorded
    Webhook->>ERP: Dispatch HMAC-Signed Payload
```

---

## 📌 Flow 8: Negative Proof & Tamper Detection Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor Attacker as Malicious Actor
    participant Lab as Verification Lab (/admin/verification-lab)
    participant Engine as Negative Proof Engine

    Attacker->>Lab: Submit Altered Degree Credential (e.g. CGPA 6.0 -> 9.8)
    Lab->>Engine: Compute Canonical RFC 8785 SHA-256 Digest
    Engine->>Engine: Compare with Original Signature Digest
    Engine-->>Lab: Reject with DIGEST_INTEGRITY_CHECK Failure (Status: INVALID)
```
