# Architecture

```text
Citizen web app
      |
      | HTTPS / JSON
      v
API gateway + diagnostic orchestration
      |
      +-- diagnostic rules
      +-- audit-event abstraction
      +-- consented government/issuer adapters (future)
      |
      v
Minimal, encrypted operational store (future)
```

## Bounded contexts

| Context | Responsibility |
| --- | --- |
| Journey | Captures the user's declared document-recovery goal. |
| Diagnostics | Models the end-to-end stages and fault classification. |
| Recovery | Selects a clear, non-deceptive next action. |
| Integration | Isolates each consented external system adapter. |
| Audit | Records privacy-minimised event metadata and support evidence. |

## Design decisions

1. **API contracts are versioned first.** The web app never relies on provider-specific payloads.
2. **Adapters are isolated.** A failure in an issuer integration is observable without exposing underlying credentials or documents.
3. **No sensitive government credentials pass through DigiIn.** Official authentication remains in the official service.
4. **A successful flow is end-to-end.** Availability is measured through `identity -> issuer -> document -> consent -> callback`, not a single system’s uptime.
