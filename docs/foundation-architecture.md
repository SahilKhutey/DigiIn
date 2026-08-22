# DigiIn Foundation Architecture

## Architectural decision

DigiIn is a **modular monolith** for the BWM prototype. The primary object is a citizen document transaction—not a document wallet. A transaction can be diagnosed, retried, recovered, audited and completed across identity, issuer, verification and requester boundaries.

```text
Citizen intent → document discovery → transaction
                                  ├─ consent preview
                                  ├─ issuer adapter
                                  ├─ verification (future authorised integration)
                                  └─ diagnosis → retry / fallback / support evidence
```

## Implemented modules

| Module | Responsibility | Location |
| --- | --- | --- |
| Domain | Canonical transaction, failure, issuer-health, consent and document models | `services/api/app/domain` |
| Catalogue | Intent-first document discovery using mock taxonomy | `services/api/app/services/catalogue.py` |
| Recovery | Transaction state, fault taxonomy, diagnosis and recovery policy | `services/api/app/services/recovery.py` |
| Trust | Consent preview and mock issuer health | `services/api/app/services/trust.py` |
| Integration | Provider-neutral issuer adapter protocol and mock adapter | `services/api/app/integrations/issuer.py` |
| API | Versioned FastAPI routes only; orchestration does not live in route handlers | `services/api/app/main.py` |

## Current API surface

| Endpoint | Role |
| --- | --- |
| `GET /api/v1/documents?q=` | Intent-first document catalogue search |
| `GET /api/v1/documents/{id}` | Document-type trust metadata |
| `GET /api/v1/transactions/{id}/diagnosis` | Explainable transaction outcome |
| `POST /api/v1/transactions/{id}/retry` | Mock targeted retry |
| `GET /api/v1/issuers/health` | Mock issuer health monitoring |
| `GET /api/v1/consents/preview` | Plain-language consent preview |

## Implemented failure taxonomy

- `IDENTITY_MISMATCH`
- `ISSUER_TIMEOUT`
- `CALLBACK_FAILED`
- `JOURNEY_COMPLETE`

Each prototype fault provides a citizen-facing explanation, accountable owner, recovery action, opaque support reference and fallback availability.

## Next modules requiring authorised integration

- OIDC/PKCE session identity and device management.
- Persistent PostgreSQL transaction/event/audit storage.
- Digital signature, QR, URI and hash verification.
- Consent grant/revoke enforcement.
- Issuer and requester partner sandbox, certification and mTLS.
- Official fallback registry with authorised links and verification dates.

These are deliberately not faked. No live government source, identity credential, legal verification, OTP, Aadhaar identifier, or document file is processed by this prototype.
