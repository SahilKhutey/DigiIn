# DigiIn — Phase 11: Backend & Data Foundation

Persistent, multi-tenant sovereign backend architecture connecting PostgreSQL, Redis, Fastify API, and React frontend.

## Key Subsystems

1. **PostgreSQL & Prisma Schema (`prisma/schema.prisma`)**:
   - 16 production models: `User`, `Organisation`, `OrganisationUser` (RBAC), `Session`, `VerificationRequest`, `Consent`, `Document`, `Verification`, `VerificationResult`, `VerificationProof`, `Permission`, `ApiClient`, `ApiCredential`, `Webhook`, `AuditEvent`, `Notification`.
2. **Fastify API Server (`apps/api/`)**:
   - Modular domain structure: `auth`, `identity`, `organisations`, `requests`, `consent`, `documents`, `verification`, `proofs`, `permissions`, `notifications`, `webhooks`, `audit`, `developer`.
   - Consent enforcement middleware returning `403 CONSENT_REQUIRED`.
   - Webhook HMAC-SHA256 signing and replay protection.
   - OpenAPI v1 contract (`apps/api/openapi.yaml`).
3. **Containerized Stack (`docker-compose.yml`)**:
   - PostgreSQL (5432), Redis (6379), Fastify API (8080), React Web (3000).

## Run with Docker

```bash
docker compose up -d
```
