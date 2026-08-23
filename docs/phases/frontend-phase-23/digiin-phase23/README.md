# DigiIn — Phase 23: Privacy, Data Governance & Compliance

Executable privacy-by-design policy engine, data classification inventory, machine-enforceable consent, attribute-level minimization, automated retention, legal holds, citizen data export, 6-stage account closure, and privacy auditing.

## Key Subsystems

1. **Data Classification & Asset Registry (`DataAssetRegistry`)**:
   - Classifies assets from `PUBLIC` to `CRYPTOGRAPHIC_SECRET` with assigned ownership and retention profiles.
2. **Purpose Limitation Registry (`DataPurposeRegistry`)**:
   - Maps permissible data classifications to legitimate operational purposes.
3. **Machine-Enforceable Consent Engine (`ConsentPolicyEngine`)**:
   - Enforces purpose binding, scope containment, time-bound validity, and instant revocation.
4. **Data Minimizer (`DataMinimizer`)**:
   - Converts raw evidence documents into minimal verifiable claims (e.g. `degree.verified: true`).
5. **Retention Engine & Legal Holds (`RetentionScheduler`)**:
   - Evaluates automated record expiration while strictly respecting active `LegalHold` locks.
6. **Citizen Data Export & Account Closure (`DataExportService`, `AccountClosureManager`)**:
   - Generates DPDP-compliant data export archives and executes the 6-stage account closure pipeline.
7. **Privacy Audit Logger (`PrivacyAuditLogger`)**:
   - Records zero-PII audit events for all sensitive data access, specifically logging unauthorized and denied attempts.
8. **Compliance Control Registry (`ComplianceRegistry`)**:
   - Tracks DPDP Act 2023, ISO 27701, and GDPR compliance controls and evidence references.

## Run with Docker

```bash
docker compose up -d
```
