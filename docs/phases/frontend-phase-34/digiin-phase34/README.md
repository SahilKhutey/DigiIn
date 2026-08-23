# DigiIn — Phase 34: Services Working + User Interface + Department & Institutional Requests/Review

Institutional Operating Layer for government departments, universities, employers, financial institutions, and licensing bodies: Organization & Department Hierarchy, Scoped Institutional RBAC, Request Templates, Departmental Request Wizard, Institutional Review Queue (`/institution/review`), Separation of Verification vs Institutional Decisions (`Approved`, `Rejected`, `Escalated`), Chronological Request Timelines, HMAC-Signed Webhooks, and Multi-Level Analytics.

## Key Subsystems

1. **Organization & Department Hierarchy (`OrganizationHierarchyManager`)**:
   - Manages organizations, sub-departments, institutional users, and role permissions across 5 roles (`ORG_ADMIN`, `DEPARTMENT_ADMIN`, `REVIEWER`, `OPERATOR`, `VIEWER`).
2. **Request Template Engine (`RequestTemplateManager`, `RequestTemplate`)**:
   - Reusable request templates with pre-configured purposes, required claims, assurance levels, and disclosure modes (`MINIMAL`, `SELECTIVE`, `FULL`).
3. **Department Request Wizard (`DepartmentRequestEngine`)**:
   - Department-scoped verification request creation wizard.
4. **Institutional Review Queue & Decisions (`InstitutionalReviewManager`)**:
   - Ingests verified requests, enables departmental review, and records separate institutional decisions (`APPROVED`, `REJECTED`, `ESCALATED`).
5. **Chronological Request Timeline**:
   - Full auditable progression from request creation to citizen consent, verification, review, and final decision.
6. **HMAC-Signed Webhooks & Analytics (`InstitutionalWebhookDispatcher`, `InstitutionalDashboardService`)**:
   - Dispatches signed event payloads to external ERPs with replay protection nonces.

## Run with Docker

```bash
docker compose up -d
```
