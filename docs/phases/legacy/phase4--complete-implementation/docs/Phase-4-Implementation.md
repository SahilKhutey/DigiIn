# DigiIn Phase 4 — Verification & Credential Engine

## Objective

Convert verified document claims into durable DigiIn credentials with explicit provenance, verification state, issuance, revocation, and independent verification.

## Trust model

Document evidence is not itself a credential.

```text
Evidence → Extracted Claims → Verification Decision → Credential → Proof
```

A credential is issued only after an authorized verification decision.

## Core entities

### VerificationCase
Tracks the verification lifecycle:
- subject/account
- document/version
- verification type
- status
- assigned reviewer
- decision
- timestamps

### VerifiedClaim
A normalized claim with:
- claim type
- value/reference
- source
- verification level
- verification case
- verified timestamp

### Credential
A durable credential:
- credential ID
- account
- credential type
- issuer
- claims
- issuance timestamp
- expiration
- status
- source verification case

### Revocation
Credential status must support:
- ACTIVE
- SUSPENDED
- REVOKED
- EXPIRED

Revocation is append-only and auditable.

## Credential issuance invariant

No credential may be issued unless:
1. the verification case is approved;
2. the subject owns the source evidence;
3. all required claims are verified;
4. the issuer is authorized;
5. the credential ID is unique;
6. the issuance event is audited.

## Verification

A verifier must be able to submit a credential/proof and receive:
- valid/invalid
- issuer
- subject/account reference as policy permits
- credential type
- claim verification result
- status
- issued/expiry timestamps
- revocation status

The verification response must not reveal claims beyond the requested/policy-approved disclosure.

## API target

POST /api/v1/verification/cases
GET  /api/v1/verification/cases/{id}
POST /api/v1/verification/cases/{id}/approve
POST /api/v1/verification/cases/{id}/reject

POST /api/v1/credentials/issue
GET  /api/v1/credentials
GET  /api/v1/credentials/{id}
POST /api/v1/credentials/{id}/revoke

POST /api/v1/credentials/verify

## Exit criteria

A complete test can:
1. create an evidence-backed verification case;
2. approve it;
3. issue a credential;
4. verify the credential;
5. revoke it;
6. demonstrate that verification rejects the revoked credential.
