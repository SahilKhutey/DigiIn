# DigiIn Role-Based Access Control & Resource Ownership Specification

## 1. System Roles

1. **`CITIZEN`**: Individual account holder managing documents, granting/revoking consent, and reviewing activity.
2. **`ORG_USER` / `VERIFIER`**: Relying party representative reviewing completed verification requests.
3. **`ORG_ADMIN`**: Institutional administrator managing organisation users, API credentials, and webhooks.
4. **`REVIEWER`**: Official reviewer inspecting legacy document OCR evidence in government review queues.
5. **`DEVELOPER`**: Technical integration engineer managing API keys and simulated webhook delivery.
6. **`ADMIN`**: Platform administrator managing provider health, integration toggles, and system audit logs.

---

## 2. Granular Permissions Matrix

| Permission | Description | Allowed Roles |
| :--- | :--- | :--- |
| `document:read` | Inspect citizen document metadata | `CITIZEN` (Own), `REVIEWER`, `ADMIN` |
| `document:upload` | Ingest new document binary | `CITIZEN`, `ADMIN` |
| `document:delete` | Delete uploaded document | `CITIZEN` (Own), `ADMIN` |
| `verification:create` | Issue verification request | `ORG_USER`, `ORG_ADMIN`, `ADMIN` |
| `verification:read` | Inspect verification outcome | `ORG_USER`, `ORG_ADMIN`, `REVIEWER`, `ADMIN` |
| `consent:create` | Grant purpose-bound consent | `CITIZEN`, `ADMIN` |
| `consent:revoke` | Revoke active consent grant | `CITIZEN`, `ADMIN` |
| `proof:create` | Mint cryptographic proof token | `CITIZEN`, `ADMIN` |
| `proof:verify` | Validate cryptographic proof | All Roles & Public Endpoints |
| `api:manage` | Create/rotate API keys | `ORG_ADMIN`, `DEVELOPER`, `ADMIN` |
| `audit:read` | View immutable audit trail | `ORG_ADMIN`, `ADMIN` |
| `system:admin` | Manage providers & platform config | `ADMIN` |

---

## 3. IDOR Defense & Multi-Tenant Scoping Rule

Role authorization is **necessary but not sufficient**. Every sensitive resource access must also satisfy:
```python
# Citizen Scoping
if actor.role == "CITIZEN":
    assert resource.citizen_id == actor.user_id

# Organisation Multi-Tenant Scoping
if actor.role in ("ORG_USER", "ORG_ADMIN", "DEVELOPER"):
    assert resource.organisation_id == actor.organisation_id
```
Attempts to bypass ownership return `403 FORBIDDEN_IDOR` or `403 FORBIDDEN_TENANT_ISOLATION`.
