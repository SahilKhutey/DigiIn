# Implementation Map

## Core domains

- Identity/Auth: `app/api/v1/auth.py`, `app/core/security.py`
- Citizen: `app/api/v1/citizen.py`
- Verification: `app/services/verification.py`
- Issuers: `app/integrations/issuer.py`
- Proofs: `app/api/v1/proofs.py`
- Government review: `app/api/v1/government.py`
- Audit: `app/services/audit.py`
- Data model: `app/models/entities.py`

## Next production modules

1. Object storage adapter + signed upload URLs
2. Antivirus/file validation
3. OCR worker
4. Document classification
5. Real issuer adapter SDK
6. OIDC authorization server
7. Passkeys/WebAuthn
8. KMS/HSM-backed signing
9. Redis durable task queue
10. Postgres migrations with Alembic
11. OpenTelemetry
12. Rate limiting
13. API gateway
14. Full requester/issuer/admin web applications
15. Multilingual content system
16. WCAG 2.2 AA automated + manual testing
17. Mobile secure storage and biometric unlock
18. Disaster recovery and retention policies
