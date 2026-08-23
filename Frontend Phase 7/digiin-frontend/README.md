# DigiIn Frontend — Phase 7: Digital Verification Proof & Sharing

UX4G-aligned frontend foundation for DigiIn's **Digital Verification Proof & Sharing Layer**.

## Phase 7 Overview

Phase 7 connects the completed verification to relying organizations:
1. **Verification Proof**: RFC 7515/7519 Ed25519 signed credential assertion.
2. **Multi-Channel Sharing**:
   - Verification ID (`DIN-VRF-82A91-K7`).
   - Secure Share Link (`#/verify/proof/DIN-VRF-82A91-K7`).
   - Offline Asymmetric Proof QR code.
3. **Public Verifier Portal (`#/verify/proof/:id`)**:
   - Institutional portal for ABC University Admissions.
   - Cryptographic signature check with government gateway public key (`digiin-ed25519-key-2026`).
   - Zero-Knowledge predicate assertions verified without storing raw document copies.

## Run Locally

```bash
python -m http.server 4179
```

Open `http://localhost:4179`.
