# DigiIn Frontend — Phase 9: Identity, Trust & API Foundation

UX4G-aligned frontend foundation for DigiIn's **Identity, Trust & API Foundation**.

## Phase 9 Overview

Phase 9 establishes the infrastructure that makes DigiIn secure, reusable, auditable, and API-ready:
1. **Three Distinct Sovereign Identifiers**:
   - **DigiIn ID** (`DIN-7K4P-92M8`): Identifies a citizen account.
   - **Verification ID** (`DIN-VRF-82A91-K7`): Identifies a specific verification transaction.
   - **Proof ID** (`DIN-PRF-51Q8-X2`): Identifies a shareable, verifiable result.
2. **Citizen Identity & Privacy Hub**:
   - `/account/identity`: Identity presentation.
   - `/privacy/permissions`: Purpose-bound permission management & revocation.
   - `/privacy/organisations`: Connected organisations list.
   - `/privacy`: Comprehensive privacy hub.
3. **Security Centre & Audit Log**:
   - `/security`: Security health, active sessions & remote sign-out.
   - `/security/activity`: Unified audit timeline.
4. **Developer Portal & API Foundation**:
   - `/organisation/developer`: Developer metrics and overview.
   - `/organisation/developer/credentials`: Scoped API clients and one-time secret display.
   - `/organisation/developer/webhooks`: Webhook management.
   - `/organisation/developer/docs`: API v1 specification.
   - `/organisation/developer/console`: Interactive API Request Simulator.

## Run Locally

```bash
python -m http.server 4181
```

Open `http://localhost:4181`.
