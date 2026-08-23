# DigiIn — Phase 28: Ecosystem Adoption & Institutional Scale

Institutional portal, organization RBAC, reusable onboarding state machine (Draft to Production), automated 9-point accreditation engine, public service directory & integration marketplace, multi-environment developer application management, zero-downtime credential rotation with grace periods, institutional SLA & operations tracking, legacy document migration framework, and integration certification test harness.

## Key Subsystems

1. **Institutional RBAC (`InstitutionalRBACGuard`)**:
   - Enforces granular permission boundaries across 7 organizational roles (`OWNER`, `ADMIN`, `TRUST_ADMIN`, `SECURITY_ADMIN`, `DEVELOPER`, `AUDITOR`, `VIEWER`).
2. **Onboarding State Machine (`OnboardingWorkflowEngine`)**:
   - Manages the 10-stage institutional onboarding journey from `DRAFT` to `PRODUCTION`.
3. **Automated Accreditation Engine (`AutomatedAccreditationChecker`)**:
   - Evaluates 9 mandatory institutional criteria with auditable trail records.
4. **Service Directory & Marketplace (`ServiceDirectory`, `IntegrationMarketplace`)**:
   - Public zero-PII service discovery and standardized integration package templates.
5. **Developer Platform & Credential Lifecycle (`CredentialLifecycleManager`)**:
   - Multi-environment isolation (`SANDBOX`, `STAGING`, `PRODUCTION`) with zero-downtime rotation and grace periods.
6. **Institutional SLA & Operations (`InstitutionalSLAManager`)**:
   - Monitors latency SLOs (p95 < 500ms), availability (> 99.9%), and SEV1-SEV4 incidents.
7. **Legacy Document Migration Framework (`MigrationFramework`)**:
   - Normalizes legacy database archives into standardized verified claims via batch pipelines.
8. **Integration Certification Engine (`IntegrationCertificationEngine`)**:
   - Automated 7-point test harness required before granting production authorization.
9. **Role-Based Institutional Analytics (`InstitutionalAnalytics`)**:
   - Dedicated operational telemetry for Issuers and Verifiers.

## Run with Docker

```bash
docker compose up -d
```
