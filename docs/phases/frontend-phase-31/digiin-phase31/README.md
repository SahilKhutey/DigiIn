# DigiIn — Phase 31: Working Product & User Request Handling

Intent-driven request pipeline, standard request and response envelopes (`DigiInRequest<T>`, `DigiInResponse<T>`), 7-stage request lifecycle state machine, idempotency manager with deduplication, normalized `AuthContext` with fine-grained authorization, 3 core production workflows (Document Upload & Verification, Institutional Request & Citizen Consent, Credential Issuance & Presentation), unified notification manager, activity history (`/dashboard/activity`), and user-friendly error shielding.

## Key Subsystems

1. **Standard Request Pipeline (`DigiInRequest`, `DigiInResponse`, `IdempotencyManager`)**:
   - Enforces uniform request envelopes with `requestId`, actors, context, and deduplication via `Idempotency-Key`.
2. **User Action Router (`UserActionRouter`)**:
   - Central intent dispatcher routing UI actions to workflow handlers.
3. **Authentication Context & Granular Authorization (`AuthContext`, `AuthorizationGuard`)**:
   - Normalized security context enforcing fine-grained resource and purpose authorizations.
4. **Flow 1: Document Upload & Verification Workflow (`DocumentVerificationWorkflow`)**:
   - Document upload $\rightarrow$ security validation $\rightarrow$ authoritative verification $\rightarrow$ audit $\rightarrow$ activity history.
5. **Flow 2: Institutional Request & Citizen Consent Workflow (`InstitutionalConsentWorkflow`)**:
   - Institution request $\rightarrow$ citizen consent review $\rightarrow$ purpose-bound approval $\rightarrow$ presentation proof token.
6. **Flow 3: Credential Issuance, Presentation & Revocation (`CredentialPresentationWorkflow`)**:
   - Issuer issuance $\rightarrow$ citizen presentation $\rightarrow$ verifier check $\rightarrow$ instant revocation propagation.
7. **Unified Notifications & Activity History (`NotificationManager`, `ActivityHistoryManager`)**:
   - Real-time in-app notifications and activity timeline for citizen dashboard (`/dashboard/activity`).
8. **User-Friendly Error Shielding (`ErrorSanitizer`, `DigiInError`)**:
   - Sanitizes raw internal exceptions and SQL/stack traces into clear, safe user messages.

## Run with Docker

```bash
docker compose up -d
```
