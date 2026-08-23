# DigiIn Frontend — Phase 10: Platform Integration & Operations

UX4G-aligned frontend foundation for DigiIn's **Platform Integration, Observability & Platform Operations**.

## Phase 10 Overview

Phase 10 connects all prior phases (1–9) into a production-ready integration, notification, observability, and operations layer:
1. **Domain Event Bus (`src/services/events/`)**: Decoupled publisher-subscriber messaging connecting verifications, consent, proofs, and audit logs.
2. **Citizen & Organisation Notification Centers**:
   - `/notifications`: Actionable notifications with direct links to transactions.
   - `/settings/notifications`: Channel preferences (In-app, Email, SMS).
   - `/organisation/notifications`: Real-time transaction and webhook delivery alerts.
3. **Webhook Delivery System (`src/services/webhooks/`)**:
   - Webhook delivery inspection (`/organisation/developer/webhooks`) with attempt logging and exponential retry simulation.
4. **API Usage Analytics & Rate Limiting (`/organisation/developer/usage`)**:
   - Real-time traffic breakdown (1,284 Requests Today, 97.9% success rate) and 429 rate limit telemetry.
5. **System Health & Observability Console (`/admin/system`)**:
   - Live status of API Gateway, Verification Service, Proof Service, Notification Service, Webhook Gateway, and Audit Service.
6. **Public Service Status Page (`/status`)**:
   - Accessible user-facing uptime indicator and latency monitoring.
7. **Platform Integrations Dashboard (`/organisation/integrations`)**:
   - Connector overview for DigiLocker, Verification Engine, and Notification Hub.

## Run Locally

```bash
python -m http.server 4182
```

Open `http://localhost:4182`.
