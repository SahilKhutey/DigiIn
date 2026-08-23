# DigiIn — Phase 24: Performance, Scalability & High-Load Engineering

High-throughput scalability mesh, granular dependency latency timers, safe reference caching, cursor-based pagination, multi-queue worker scaling governor, provider circuit breakers, distributed token-bucket rate limiting, cryptographic idempotency deduplication, and resumable chunked upload orchestrator.

## Key Subsystems

1. **Performance Context & Dependency Timers (`PerformanceContext`, `DependencyTimer`)**:
   - Sub-millisecond timing of pipeline stages (Auth, Policy, DB, Provider, Serialization) with budget evaluation.
2. **Safe Tiered Cache (`SafeTieredCache`)**:
   - High-speed in-memory LRU/TTL caching for non-sensitive reference metadata with instant invalidation (strictly no PII).
3. **Query Optimizer & Cursor Paginator (`CursorPaginator`, `ResponseProjector`)**:
   - Deterministic cursor-based pagination and field-level projection eliminating N+1 queries.
4. **Multi-Queue Scaling Governor (`QueueScalingGovernor`)**:
   - Dynamic worker concurrency scaling based on backlog depth with backpressure mitigation.
5. **Provider Rate Limiting & Circuit Breakers (`ProviderCircuitBreaker`, `ExponentialBackoffRetry`)**:
   - 3-state circuit breaker (`CLOSED` $\rightarrow$ `OPEN` $\rightarrow$ `HALF_OPEN`) and exponential retry with jitter.
6. **Distributed Rate Limiting (`DistributedRateLimiter`)**:
   - Multi-dimensional token-bucket rate limiting across IP, user, organization, and API client.
7. **Idempotency Engine (`IdempotencyEngine`)**:
   - Cryptographic request hashing preventing duplicate execution and redundant proof minting during network retries.
8. **Resumable Chunked Direct Upload (`ChunkedUploadManager`)**:
   - Multi-part chunked upload orchestrator with parallel assembly and SHA-256 validation.

## Run with Docker

```bash
docker compose up -d
```
