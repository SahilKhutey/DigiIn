# DigiIn — Phase 22: Production Infrastructure & Deployment

Production infrastructure as code (IaC), multi-stage CI/CD pipelines, KMS envelope encryption, private object storage with presigned URLs, connection pooling, canary rollouts with instant rollback, and disaster recovery verification.

## Key Subsystems

1. **Environment Segregation (`EnvironmentManager`)**:
   - Strict isolation across `DEVELOPMENT`, `STAGING`, and `PRODUCTION` environments.
2. **KMS Envelope Encryption (`KmsSecretManager`)**:
   - Cryptographic domain separation for Database, Document Storage, Secrets, and Proof-signing keys.
3. **Private Encrypted Object Storage (`PrivateObjectStorageClient`)**:
   - S3-compatible client issuing short-lived (300s) presigned upload URLs with 10MB file caps.
4. **Database Pool Governor & Migration Validator (`DatabasePoolGovernor`, `MigrationPlanValidator`)**:
   - Protects PostgreSQL connection limits and validates zero-downtime Expand/Contract schema migrations.
5. **Canary Rollout Orchestrator (`DeploymentOrchestrator`)**:
   - Canary progression (5% $\rightarrow$ 25% $\rightarrow$ 50% $\rightarrow$ 100%) and instant single-command rollback to immutable artifact digests (`sha256:...`).
6. **Disaster Recovery Engine (`DisasterRecoveryEngine`)**:
   - Automated DR drill validating database restore, KMS key recovery, and post-restore cryptographic proof verification.
7. **Edge WAF & Cache Policy (`EdgeWafEngine`)**:
   - Filters SQLi/XSS attacks, enforces 2MB API body limits, and mandates `Cache-Control: no-store` on sensitive verification endpoints.

## Run with Docker

```bash
docker compose up -d
```
