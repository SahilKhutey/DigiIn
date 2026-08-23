# DigiIn — Phase 12: Real DigiLocker Integration & Document Pipeline

Server-controlled, cryptographic document acquisition and verification pipeline connecting DigiLocker, Redis queues, and Fastify API.

## Key Subsystems

1. **DigiLocker OAuth & Provider Abstraction (`apps/api/src/modules/digilocker/`)**:
   - OAuth state machine (`OAuthState`) with AES-256-GCM token encryption. Tokens never touch the browser.
2. **Document Discovery, Selection & Normalization (`GET /v1/digilocker/documents`)**:
   - Discovers available credentials across education, identity, address, and driving categories.
3. **Cryptographic Checksum & Provenance (`DocumentProvenance`)**:
   - SHA-256 binary checksum computed upon background retrieval.
4. **Two-Tiered Authorization Isolation**:
   - Strict separation: DigiLocker Consent (DigiIn $\leftrightarrow$ DigiLocker) vs. Organisation Consent (Citizen $\leftrightarrow$ Organisation). Organisations cannot browse raw citizen vaults.
5. **Prisma & PostgreSQL Schema (`prisma/schema.prisma`)**:
   - `DigiLockerConnection`, `OAuthState`, `Document`, `DocumentProvenance`, `DocumentJob`, `VerificationResult`.
6. **OpenAPI Specification (`openapi.yaml`)**:
   - Endpoints for DigiLocker OAuth, document discovery, retrieval, and verification jobs.

## Run with Docker

```bash
docker compose up -d
```
