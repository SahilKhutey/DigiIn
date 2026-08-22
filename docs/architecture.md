# Architecture

```text
Citizen web app
      |
      | HTTPS / JSON
      v
API gateway + lifecycle orchestration
      |
      +-- document catalogue
      +-- transaction diagnosis
      +-- trust and consent
      +-- verification engine (future)
      +-- correction/versioning (future)
      +-- legacy digitization (future)
      +-- consented government/issuer/requester adapters (future)
      |
      v
Encrypted operational store and audit log (future)
```

## Bounded contexts

| Context | Responsibility |
| --- | --- |
| Document center | Captures the user's declared need: receive, upload, verify, correct, share or recover. |
| Provenance | Separates document source, file evidence, versions and authority relationships. |
| Verification | Matches identity, issuer, registry, signature, QR, metadata, historical records and human review. |
| Diagnostics | Models end-to-end stages and fault classification. |
| Recovery | Selects a clear, non-deceptive next action for failed document journeys. |
| Correction | Preserves original versions and manages government or issuer correction cases. |
| Sharing | Issues minimum-disclosure proofs with consent. |
| Integration | Isolates each consented external system adapter. |
| Audit | Records privacy-minimised event metadata and support evidence. |

## Design decisions

1. **API contracts are versioned first.** The web app never relies on provider-specific payloads.
2. **Adapters are isolated.** A failure in an issuer integration is observable without exposing underlying credentials or documents.
3. **No sensitive government credentials pass through DigiIn.** Official authentication remains in the official service.
4. **Document is not file.** Files are evidence; provenance, verification, validity and version history define trust.
5. **A successful recovery flow is end-to-end.** Availability is measured through `identity -> issuer -> document -> consent -> callback`, not a single system's uptime.
6. **AI assists but does not decide authority.** OCR, classification and matching can recommend; authorised bodies decide final verification and correction outcomes.
