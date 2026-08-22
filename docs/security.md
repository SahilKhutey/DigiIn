# Security and privacy baseline

## Non-negotiable controls

- Do not request, log, cache, or display Aadhaar numbers, OTPs, passwords, PINs, or full identity documents.
- Use explicit consent before any future third-party data request; make scopes and retention understandable.
- Encrypt data in transit and at rest; store only the minimum metadata required for recovery support.
- Redact identifiers from logs and telemetry. Use a short-lived, opaque journey ID instead of personal identifiers.
- Enforce least privilege, service-to-service authentication, rate limits, dependency timeouts, and audit trails.
- Complete a threat model, DPIA, accessibility review, and authorised integration review before pilot deployment.

## Incident posture

The future production service should provide structured error codes to clients, retain internal correlation IDs, and publish status without exposing provider details or citizen data.
