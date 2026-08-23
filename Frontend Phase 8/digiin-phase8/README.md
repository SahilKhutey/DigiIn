# DigiIn Frontend — Phase 7

Digital Verification Proof + Secure Sharing Layer.

## Implemented
- Create a privacy-minimized verification proof from Phase 6 results
- Proof lifecycle: active, expired, revoked
- Proof details and verified-document summary
- Secure share URL generation
- QR verification presentation (dependency-free demo visual)
- Organisation proof verification flow
- Valid / invalid / expired / revoked validation states
- Citizen proof revocation
- Proof audit events
- Backend-ready proof service boundary

## Run

```bash
npm run dev
```

The prototype uses simulated services. No real DigiLocker credentials, documents, or production verification endpoints are used.

## Phase 8 — Organisation Portal

Adds the two-sided organisation experience:
- organisation demo authentication and route protection
- organisation dashboard and statistics
- verification request creation with citizen DigiIn ID, purpose, documents and validity
- request review, lifecycle, list/filter/detail/cancel
- consent and verification status visibility
- proof verification integration
- organisation history and profile
- privacy boundary: DigiIn ID is not document access

Demo organisation: `ORG-84K2-19Q7` / `verification@abcuniversity.example` / any password.
