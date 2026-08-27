# DigiIn Sovereign Account ID Specification

## Executive Summary

The **DigiIn Sovereign Account ID** is a human-friendly, cryptographically secure identifier designed for nationwide digital public infrastructure. It serves as the universal account alias for citizens interacting with government services, enabling instant verification without repeated document uploads.

---

## 1. Character Length & Format

```text
DI-XXXX-XXXX-XXXX
Example: DI-7K4M-9Q2X-8P6R
```

- **Prefix**: `DI-` (National DigiIn Identifier)
- **Random Blocks**: 3 groups of 4 characters (`XXXX-XXXX-XXXX`)
- **Total Display Length**: 17 characters including prefix and hyphens (14 characters in the random suffix block).
- **Group Separation**: 4-character blocks optimized for verbal dictation, mobile screens, paper printing, and OCR transcription.

---

## 2. Character Set & Entropy

- **Alphabet**: Human-friendly Base32 (32 characters):
  ```text
  ABCDEFGHJKLMNPQRSTUVWXYZ23456789
  ```
- **Excluded Characters**: `0` (zero), `1` (one), `I` (capital i), `O` (capital o).
  - *Rationale*: Eliminates transcription errors across handwriting, low-resolution screens, and voice communication.
- **Keyspace Entropy**:
  $$\text{Total Combinations} = 32^{12} \approx 1.15 \times 10^{18}$$
  Provides practically unlimited address space for national scale while preventing enumeration attacks.

---

## 3. Security Invariants: Identifier vs Authenticator

> [!IMPORTANT]
> **The DigiIn ID is an Identifier, NOT an Authenticator.**
> Knowing a citizen's DigiIn ID (`DI-7K4M-9Q2X-8P6R`) alone grants **zero access** to any documents or attributes.

```
DigiIn ID Provided
       │
       ▼
Identify Account
       │
       ▼
Authenticate Requester (Mutual TLS / API Key)
       │
       ▼
Authorize Requester (Accredited Scope Check)
       │
       ▼
Check Purpose & Scope Limitation
       │
       ▼
Obtain Explicit Citizen Consent
       │
       ▼
Return Minimum Required Information (Zero Raw Files Transferred)
```

### Security Features
1. **Opaque & Non-Semantic**: Contains zero PII (no Aadhaar, DOB, name, phone, caste, or state codes).
2. **Non-Sequential**: Cryptographically random generator (`secrets.choice`) prevents enumeration scanning.
3. **Anti-Enumeration Guard**: Automated IP and tenant rate limiting with uniform-timing error responses.
4. **Tamper-Evident Audit Logging**: Every query attempt, whether successful or denied, is logged to the citizen's sovereign audit trail.

---

## 4. Dual Identity Architecture

DigiIn enforces strict separation between citizen-facing public aliases and system-facing primary keys:

```text
                DigiIn Account
                      │
          ┌───────────┴───────────┐
          │                       │
   Public Account ID       Internal Account ID
   DI-7K4M-9Q2X-8P6R       UUIDv7 / UUID4
          │                       │
    Citizen-facing           System-facing
  (Forms, Kiosks, UI)     (DB PK, Cryptography)
```

---

## 5. Ephemeral Verification Code (2FA / Kiosk Mode)

For counter interactions or physical citizen service centers (CSCs), citizens can generate a **Temporary Verification Code**:

- **Format**: 6-digit numeric OTP (e.g., `482913`)
- **Validity Window**: 10 minutes (600 seconds)
- **Security**: Cryptographically hashed using HMAC-SHA256 with server-side salt.
- **Workflow**: Citizen gives `DigiIn ID + Temporary Code` to the service desk operator, eliminating long-term delegation risks.

---

## 6. Secure QR Code Specification

The citizen dashboard and mobile app display a QR code containing an ephemeral signed verification request token rather than static document dumps:

```text
digiin://verify?id=DI-7K4M-9Q2X-8P6R&t=1772088000&code=482913&sig=a8f4c2...
```

- **Validity**: Short-lived (300 seconds).
- **Contents**: Account ID + Timestamp + Temporary Code + Cryptographic Signature.
- **Payload Guarantee**: Contains **0 raw document bytes**.

---

## 7. The 1-Click "Verify with DigiIn" Protocol

For web applications and digital portals:

1. **Initiate**: User clicks **"⚡ Verify with DigiIn"** on relying portal (e.g., University Admissions).
2. **Authenticate**: Citizen authenticates securely on DigiIn gateway.
3. **Review**: Citizen inspects the **Sharing Review** (Requester, Purpose, exact claims requested vs withheld).
4. **Consent & Attest**: Citizen grants consent; DigiIn emits an **Ed25519 Verifiable Proof** (RFC 7515/8032 JWS) with zero raw PDFs transferred.
5. **Return**: Relying party receives cryptographically sealed assertion instantly.
