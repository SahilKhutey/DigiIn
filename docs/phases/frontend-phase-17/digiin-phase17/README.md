# DigiIn — Phase 17: Production Backend Completion & Deterministic Workflow Engine

Authoritative domain state machines, purpose-bound claim-level consent, officer review queues with conflict-of-interest checks, transactional outbox pattern, and automated expiration sweepers.

## Key Subsystems

1. **Authoritative Domain State Machines (`DomainWorkflowEngine`)**:
   - Explicit lifecycle graphs for **Document**, **Verification**, **Consent**, **VerificationRequest**, **Proof**, and **Organisation**.
   - `transition(entity, event)` enforcing version increments and rejecting invalid transitions with `IllegalStateTransitionError`.
2. **Claim-Level Consent Engine (`ConsentEngine`)**:
   - Purpose limitation binding and granular claim grants/declines (e.g. allowing `EDUCATION` and `AGE` while declining `RESIDENCE`).
3. **Review Queues & Conflict-of-Interest (`ReviewWorkflowEngine`)**:
   - Departmental review task queues and checks preventing reviewers from approving their own documents.
4. **Transactional Outbox & Idempotency (`TransactionalOutboxService`)**:
   - Domain event stream recording (`PROOF_ISSUED`, `CONSENT_GRANTED`) and `Idempotency-Key` deduplication.
5. **Automated Expiration Sweepers (`ExpirationSweeperService`)**:
   - Scheduled sweepers transitioning expired records to `EXPIRED`.

## Run with Docker

```bash
docker compose up -d
```
