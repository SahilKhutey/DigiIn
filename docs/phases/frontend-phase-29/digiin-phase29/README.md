# DigiIn — Phase 29: National-Scale Operations & Infrastructure

Multi-region traffic routing with automated health-based failover draining, 5-tier request classification, traffic priority queue scheduling, 4-tier disaster recovery with automated restore integrity drills, isolated durable queues with DLQ, predictive capacity forecasting, centralized Security Operations Center (SOC), network-wide fraud risk graph, multi-jurisdiction compliance operations, and chaos resilience testing.

## Key Subsystems

1. **National Traffic Router (`NationalTrafficRouter`)**:
   - Manages health-aware multi-region routing across Mumbai, Hyderabad, and Delhi with automated failover draining.
2. **5-Tier Request Classification & Priority Scheduling**:
   - Classifies requests (`PUBLIC`, `AUTHENTICATED`, `INSTITUTIONAL`, `PRIVILEGED`, `SYSTEM`) and enforces strict priority (Verification Priority 1 > Background Priority 5).
3. **Disaster Recovery & Restore Drill Engine (`DisasterRecoveryManager`)**:
   - Governs 4 recovery tiers (Tier 0: Trust Verification RTO 5m/RPO 0m) and conducts automated restore integrity verification.
4. **Isolated Durable Queues & Capacity Monitoring (`NationalQueueEngine`, `CapacityForecastManager`)**:
   - Isolated queue partitions (`verification-events`, `notification-events`, `audit-events`, `risk-events`) with DLQ and predictive capacity forecasting.
5. **Security Operations Center (`SecurityOperationsCenter`)**:
   - Ingests security events, evaluates automated detection rules (token replay, key abuse, volume spikes), and coordinates incident triage.
6. **Network Fraud Risk Graph (`NetworkRiskGraphEngine`)**:
   - Calculates systemic risk scores across issuers and verifiers without exposing citizen PII.
7. **Compliance Operations (`ComplianceOperationsManager`)**:
   - Maps operational controls across regulations (DPDP Act India, IT Act 2000, ISO 27001, SOC2).
8. **Chaos Test Runner & Load Harness (`ChaosTestRunner`, `NationalLoadHarness`)**:
   - Validates the core safety invariant: degraded dependencies never produce a false positive `VERIFIED` result.

## Run with Docker

```bash
docker compose up -d
```
