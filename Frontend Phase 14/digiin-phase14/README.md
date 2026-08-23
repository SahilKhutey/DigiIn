# DigiIn — Phase 14: Organisation Platform & Consent Orchestration

Two-sided sovereign verification platform connecting institutional verifiers, purpose-bound claims, and citizen-controlled consent.

## Key Subsystems

1. **Organisation Platform & RBAC (`apps/api/src/modules/organisations/`)**:
   - Institutional onboarding, verified organisation status badge (`✓ Verified Organisation`), and multi-tenant RBAC.
2. **Verification Request Creation (`apps/api/src/modules/requests/`)**:
   - Purpose-bound request creation with required claims (`EDUCATION_VERIFIED`, `IDENTITY_VERIFIED`, etc.) and data minimisation.
3. **Citizen Request Inbox & Scoped Consent (`apps/api/src/modules/consent/`)**:
   - Transparent consent UI answering *Who, What, Why, How long* with instant grant, decline, and revocation.
4. **Claim-to-Document Matcher & Request Worker**:
   - Asynchronous worker matching requested claims to eligible retrieved documents, running verification engine, and issuing proofs.
5. **Multi-Tenant Isolation & Idempotency**:
   - Enforces `where: { organisationId }` and `where: { citizenId }` across all queries, backed by `IdempotencyRecord` keys.
6. **Prisma & PostgreSQL Schema (`prisma/schema.prisma`)**:
   - `VerificationRequest`, `VerificationRequestClaim`, `Consent`, `IdempotencyRecord`, `Organisation`, `User`.

## Run with Docker

```bash
docker compose up -d
```
