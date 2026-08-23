# DigiIn — Phase 15: Production Integration, Trust Network & Provider Adapter Layer

Decoupled provider adapter layer, normalized evidence engine, and fault-tolerant integration mesh.

## Key Subsystems

1. **Provider Adapter Architecture (`packages/integrations/`)**:
   - `EvidenceProvider` interface decoupling verification core from external providers (`SandboxAdapter`, `DigiLockerAdapter`, `GovernmentAdapter`, `InstitutionAdapter`).
2. **Normalized Evidence & Trust Registry**:
   - Standardizes external facts into `NormalizedEvidence` with assurance level tracking (`LOW`, `MEDIUM`, `HIGH`).
3. **Resilience & Fault Tolerance Pipeline**:
   - 10,000ms hard timeouts, 3-attempt exponential backoff retries, and automatic `CircuitBreaker`.
4. **Integration Webhooks & Replay Defense**:
   - HMAC-SHA256 signature verification and event deduplication via `IntegrationEvent` payload hashes.
5. **Developer API Key Management**:
   - Scoped API credentials (`din_live_<secret>`) with SHA-256 secret hashing.
6. **Admin Integration Dashboard (`/admin/integrations`)**:
   - Real-time provider health probes, connection diagnostics, and enable/disable management.
7. **Prisma & PostgreSQL Schema (`prisma/schema.prisma`)**:
   - `IntegrationProvider`, `IntegrationEvent`, `ApiKey`, and enhanced `Verification` models.

## Run with Docker

```bash
docker compose up -d
```
