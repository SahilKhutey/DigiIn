# DigiIn — Phase 19: Real Provider & Institutional Integration

Provider-neutral integration gateway connecting DigiIn to external authoritative sources (Government Departments, Universities, Examination Boards, Institutional registries).

## Key Subsystems

1. **Provider Registry & Trust Hierarchy (`CoreProviderRegistry`)**:
   - Manages providers across 4 trust tiers (`SOVEREIGN`, `STATUTORY`, `ACCREDITED`, `INSTITUTIONAL`) and 8 lifecycle states.
2. **Provider Adapter Framework (`ProviderAdapter`)**:
   - Modular adapters for CBSE Board, University of Delhi, Parivahan Ministry of Transport, and Universal Sandbox Simulator.
3. **Provider Gateway & Data Minimization (`ProviderGateway`)**:
   - Central gateway applying purpose-bound data minimization, 10s deadlines, exponential retries, and automatic circuit breaking (`CLOSED` $\rightarrow$ `OPEN` $\rightarrow$ `HALF_OPEN`).
4. **Normalized Evidence & Provenance (`EvidenceNormalizer`)**:
   - Standardizes diverse provider payloads into `ProviderEvidence` preserving immutable provenance (`sourceReference`, `retrievedAt`, `requestId`).
5. **Multi-Source Conflict Detection (`MultiSourceConflictDetector`)**:
   - Detects discrepancies between independent authoritative sources and routes them to manual review.
6. **Webhook Ingestion & Replay Defense (`WebhookReceiverService`)**:
   - HMAC-SHA256 signature verification, 5-minute timestamp validity windows, and event deduplication.

## Run with Docker

```bash
docker compose up -d
```
