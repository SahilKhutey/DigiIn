# DigiIn — Phase 21: Observability, Reliability & Production Operations

Production observability mesh, structured JSON logging with automatic PII scrubbing, metric percentiles, distributed tracing, Kubernetes liveness/readiness probes, actionable alerting (P0-P3), incident management, Dead-Letter Queue (DLQ) with safe replay, and cryptographic backup verification.

## Key Subsystems

1. **Structured Logging & PII Sanitizer (`StructuredLogger`)**:
   - Emits standardized JSON logs while automatically redacting passwords, tokens, private keys, and Aadhaar numbers.
2. **Metrics Collection & SLOs (`MetricsCollector`)**:
   - Calculates p50, p95, p99 request latencies, verification success velocity, and queue depths.
3. **Distributed Tracing (`DistributedTracer`)**:
   - Propagates trace and span contexts across API gateways, verification pipelines, and provider adapters.
4. **Health, Liveness & Readiness Probes (`HealthProbeManager`)**:
   - Exposes `/health/live` and `/health/ready` checking database, storage, queues, and provider connectivity.
5. **Alerting & Incident Management (`AlertAndIncidentManager`)**:
   - Actionable rule evaluation triggering P0-P3 alerts and managing incident resolution timelines.
6. **Dead-Letter Queue & Recovery (`DeadLetterQueueService`)**:
   - Quarantines failed jobs after max retry exhaustion and allows safe operator inspection and replay with idempotency keys.
7. **Cryptographic Backup Verification (`BackupVerifier`)**:
   - Validates backup integrity and decryptability against SHA-256 checksum manifests.
8. **Feature Flags & Canary Rollouts (`FeatureFlagManager`)**:
   - Deterministic percentage rollouts and instant subsystem maintenance mode switches.

## Run with Docker

```bash
docker compose up -d
```
