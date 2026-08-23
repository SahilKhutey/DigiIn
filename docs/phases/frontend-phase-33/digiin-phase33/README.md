# DigiIn — Phase 33: Working Verification $\rightarrow$ User Workflow $\rightarrow$ Service Verification $\rightarrow$ Web App

Full verification loop between external institutions and citizens: Service Registry, Service Authentication & Context, 8-stage Verification Request State Machine, Citizen Request Inbox (`/dashboard/requests`), explicit `[Allow & Verify]` consent workflow, verification execution with minimal claim disclosure, QR verification requests, Service Dashboard telemetry (`/service/dashboard`), and citizen activity timeline.

## Key Subsystems

1. **Service Registry & Identity (`ServiceRegistry`, `DigiInService`)**:
   - Registers external services and issues client credentials generating authenticated `ServiceContext`.
2. **8-Stage Verification Request State Machine (`ServiceVerificationRequest`, `RequestLifecycleStatus`)**:
   - Manages request transitions: `CREATED` $\rightarrow$ `DELIVERED` $\rightarrow$ `VIEWED` $\rightarrow$ `APPROVED` $\rightarrow$ `VERIFYING` $\rightarrow$ `COMPLETED` (or `DENIED`, `CANCELLED`, `EXPIRED`, `FAILED`).
3. **Citizen Request Inbox & Explicit Consent (`CitizenRequestInbox`)**:
   - Action-oriented inbox (`/dashboard/requests`) and detail view (`/requests/:id`) with explicit `[Allow & Verify]` vs `[Deny]`.
4. **Verification Workflow Coordinator (`ServiceVerificationCoordinator`)**:
   - Executes product & credential verification engine upon consent and filters minimal permitted claims.
5. **Short-Lived QR Verification (`QRServiceVerifier`, `QRServiceRequest`)**:
   - Generates and resolves short-lived signed verification QR requests (`digiin://service-verify/...`).
6. **Service Dashboard Telemetry (`ServiceDashboardService`)**:
   - Computes request volumes, verification success rates, pending requests, and audit logs.

## Run with Docker

```bash
docker compose up -d
```
