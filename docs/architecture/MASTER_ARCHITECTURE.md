# DigiIn — Master Architecture & Technical Specification

DigiIn is a national-scale, sovereign **Digital Trust and Verification Infrastructure** designed to bridge citizens, authoritative credential issuers, and verifying institutions.

---

## 🏛️ 1. Platform Reference Architecture

```mermaid
flowchart TD
    subgraph PublicWebTier[Layer 1: Public Web & Trust Registry]
        Landing["Public Website: /"] --> PublicDirectory["Public Services Directory: /services"]
        Landing --> TrustRegistry["Accredited Organizations: /organizations"]
        Landing --> HowItWorks["Workflow Guide: /how-it-works"]
    end

    subgraph CitizenAppTier[Layer 2: Sovereign Citizen Application]
        CitizenAuth["Auth: /login"] --> CitizenDash["Citizen Hub: /dashboard"]
        CitizenDash --> CredentialWallet["Credential Wallet: /credentials"]
        CitizenDash --> RequestInbox["Verification Inbox: /requests"]
        CitizenDash --> ConsentCenter["Consent Center: /consent"]
        CitizenDash --> ActivityLog["Activity Timeline: /activity"]
    end

    subgraph ServicePartnerTier[Layer 3: Service Partner Sites & Embeddable Widget]
        PartnerPortal["External Service Portal (e.g. Scholarship Portal)"] --> Widget["DigiIn Verification Widget: 'Continue with DigiIn'"]
        Widget --> AuthCode["Secure Authorization Code Flow"]
        AuthCode --> ConsentReview["Citizen Review: [Allow & Verify]"]
        ConsentReview --> MinimalClaimReturn["Minimal Verified Claim Return (Zero PII Leakage)"]
    end

    subgraph InstitutionalOperatingTier[Layer 4: Institutional Operating Portal]
        InstAuth["Auth: /institution/login"] --> InstDash["Department Hub: /institution"]
        InstDash --> StepperWizard["6-Step Request Wizard: /institution/requests/new"]
        InstDash --> ReviewQueue["Institutional Review Queue: /institution/review"]
        InstDash --> DecisionEngine["Department Decision Engine: Approved / Rejected"]
        InstDash --> WebhookDispatcher["HMAC-Signed Webhook Dispatcher"]
    end

    subgraph DigiInCoreTrustEngine[Layer 5: Core Trust & Verification Engine]
        ConsentReview & StepperWizard --> VerificationEngine["7-Point Product Verification Engine"]
        VerificationEngine --> CryptoCheck["Ed25519 Signature & SHA-256 Digest Check"]
        VerificationEngine --> TrustCheck["National Trust Registry Accreditation"]
        VerificationEngine --> LifecycleCheck["Authoritative Status & Revocation Check"]
        VerificationEngine --> PolicyCheck["Minimal Disclosure Policy Check"]
    end

    subgraph StorageAndAudit[Layer 6: Immutable Audit & Storage]
        CryptoCheck & TrustCheck & LifecycleCheck --> AuditLogger["Immutable Event Audit Logger"]
        AuditLogger --> ActivityLog
        AuditLogger --> WebhookDispatcher
    end
```

---

## 🔒 2. Core Architectural Invariants

1. **Verification Over Storage**: DigiIn is an authoritative verification intermediary, not a static document warehouse. A document in storage is never assumed valid without deterministic verification.
2. **Explicit Citizen Consent**: Services must declare purpose and request specific claims. The citizen reviews the exact fields and grants explicit, time-bounded consent (`[Allow & Verify]`).
3. **Minimal Disclosure**: Services receive only verified Boolean/attribute claims (`education.degree: VERIFIED`), without leaking unrequested PII, roll numbers, DOB, or raw document binaries.
4. **Separation of Duties**: DigiIn determines cryptographic authenticity (`VERIFIED`); the verifying department independently reviews applicant eligibility and records institutional decisions (`APPROVED` / `REJECTED`).
5. **Deterministic Proof & Anti-Tamper**: Any modification to credential payload bytes or signatures mathematically produces `INVALID`.
