# DigiIn Phase Development Plan

## Phase 1 — Production Foundation & Trust Boundaries
Goal: establish provider-neutral boundaries so demo adapters can later be replaced without rewriting the domain layer.

### Phase 1 deliverables
- Central application settings with explicit environment configuration.
- Stable opaque DigiIn Account ID generation and validation.
- Authentication and document-storage provider contracts.
- Local development adapters.
- Explicit demo/development/test/production modes.
- Tests for identifiers, configuration and provider contracts.
- Documentation separating simulated adapters from production integrations.

### Exit criteria
- No new code depends on hard-coded infrastructure assumptions.
- DigiIn Account ID does not encode phone/Aadhaar/email data.
- Auth/storage are accessed through interfaces.
- Local development works without government integrations.
- Production configuration fails closed when required security configuration is absent.

## Later phases
1. Production Foundation & Trust Boundaries
2. Real Document Ingestion & Persistent Pipeline
3. Identity & Authentication Hardening
4. Verification & Credential Issuance
5. DigiIn Account ID & Verification Gateway
6. Consent, Proof & Offline Verification Hardening
7. Government & External Integrations
8. Security, Privacy & Compliance Hardening
9. Scale, Observability & Operations
10. Hackathon/Public Demonstration Release

### End-to-end target
Citizen sign-in → document upload → processing → government review → credential issuance → wallet → department verification request → citizen consent → minimum-disclosure signed proof → independent verification → revocation/audit.
