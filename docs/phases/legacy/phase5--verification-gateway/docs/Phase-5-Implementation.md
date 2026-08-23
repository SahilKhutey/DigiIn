# DigiIn Phase 5 — Account ID Verification Gateway

## Objective

Make the DigiIn Account ID useful to external departments without exposing the citizen's raw document collection.

## Request flow

Verifier
→ verification request
→ DigiIn Account ID lookup
→ credential/policy evaluation
→ citizen consent
→ minimum-disclosure response
→ signed verification result
→ verifier validates result.

## Core entities

VerificationRequest:
- request_id
- verifier_id
- account_id
- purpose
- requested_claim_types
- status
- expires_at
- created_at

Consent:
- consent_id
- request_id
- account_id
- decision
- approved_claim_types
- granted_at
- expires_at
- revoked_at

VerificationResponse:
- response_id
- request_id
- account_id/pseudonymous subject reference according to policy
- disclosed claims
- credential references
- issuer information
- proof/signature reference
- generated_at
- expires_at

## Rules

1. A verifier never receives raw documents by default.
2. A verification request must contain a declared purpose.
3. Requested claims must be explicit.
4. Consent is bound to the request, purpose, account and claims.
5. Consent must expire.
6. Revoked consent cannot authorize disclosure.
7. The response contains only approved claims.
8. The account ID alone does not grant access.
9. Invalid/revoked/expired credentials cannot satisfy a request.
10. Every request, consent decision and response is auditable.

## API target

POST /api/v1/verification/requests
GET  /api/v1/verification/requests/{id}
POST /api/v1/verification/requests/{id}/approve
POST /api/v1/verification/requests/{id}/deny
POST /api/v1/verification/requests/{id}/revoke

POST /api/v1/verification/requests/{id}/evaluate
GET  /api/v1/verification/responses/{id}

## Exit criteria

A department can submit a purpose-bound request using a DigiIn Account ID; the citizen can approve only selected claims; the gateway returns only those claims backed by active credentials; and a revoked/expired credential or consent cannot be used.
