# DigiIn Foundation Architecture

## Foundation decision

DigiIn is a **national document lifecycle and trust platform**, not only a digital locker. The first implemented slice remains a citizen-facing recovery prototype, but the platform model is broader: documents can be issued, uploaded, digitized, verified, corrected, versioned, shared and independently checked.

The core rule is:

> A file is not trusted because it exists in the wallet. It becomes trusted because its provenance, verification state, validity and audit history are known.

## Conceptual architecture

```text
Citizen
  |
  v
Digital identity and consent
  |
  v
Document center
  |
  +-- Government-issued document
  |     |
  |     v
  |   Issuer adapter / registry / URI
  |
  +-- Citizen-uploaded document
  |     |
  |     v
  |   Verification request
  |
  +-- Legacy physical record
        |
        v
      Digitization and historical verification

All paths converge on:

Verification engine -> trust result -> wallet -> share / prove / recover
```

The implemented prototype handles the recovery and diagnosis portion of this model with synthetic data. Future authorised modules can add upload, verification, correction and government console workflows.

## Four document classes

Every document must carry an explicit provenance class.

| Class | Source | Trust meaning | Example |
| --- | --- | --- | --- |
| Government issued | Authorised issuer originates the record | The issuer is the source of truth | Driving licence, tax certificate, new degree |
| Citizen uploaded | Citizen provides a file | The file exists but is not independently verified | Scanned old birth certificate |
| Citizen uploaded and government verified | Citizen provides a file, authorised body verifies it | Authenticity has been confirmed by a recognised authority | Verified historical school certificate |
| Legacy or historical record | Physical or archival record is digitized | Trust depends on archival evidence and government review | Old land record, pre-digital certificate |

Self-upload never mutates the government source record. Verification creates a relationship between a citizen submission and an authoritative record or officer decision.

## Document lifecycle

Documents have a lifecycle independent of their files:

```text
DISCOVERED
  -> UPLOADED / ISSUED
  -> IDENTIFIED
  -> PENDING_VERIFICATION
  -> UNDER_REVIEW
  -> VERIFIED
  -> ACTIVE
  -> SUPERSEDED / EXPIRED / REVOKED
```

Failure and exception states include:

- `REJECTED`
- `NEEDS_CORRECTION`
- `RECORD_NOT_FOUND`
- `IDENTITY_MISMATCH`
- `INSUFFICIENT_EVIDENCE`
- `ISSUER_UNAVAILABLE`
- `DUPLICATE`
- `SUSPECTED_FRAUD`

## Document object versus file object

A PDF, image or scan is evidence; it is not the full document object.

```text
Document
  |
  +-- Metadata
  +-- Provenance
  +-- Subject
  +-- Issuer or claimed issuer
  +-- Verification results
  +-- Authenticity state
  +-- Current validity state
  +-- Versions
  +-- Files
        |
        +-- Original scan
        +-- OCR representation
        +-- Normalized PDF
        +-- Verification copy
```

This lets one real-world certificate have an original paper scan, extracted text, a verified digital representation and a later corrected version without destroying history.

## Trust model

DigiIn must avoid a single green checkmark. Trust is expressed through source, authenticity, validity and verification level.

| Trust state | Meaning |
| --- | --- |
| `GOVERNMENT_ISSUED` | The document originated from an authorised issuer. |
| `GOVERNMENT_VERIFIED` | A citizen-submitted or legacy record was verified by an authorised body. |
| `ISSUER_VERIFICATION` | Issuer or registry evidence exists, but final government status may be limited. |
| `CITIZEN_UPLOADED` | The citizen supplied the file and authenticity is not established. |
| `VERIFICATION_PENDING` | Verification has been requested or is under review. |
| `VERIFICATION_REJECTED` | The submitted evidence did not pass verification. |
| `VERIFICATION_UNAVAILABLE` | The platform cannot currently verify through an authorised route. |

Authenticity and validity are separate. A licence can be authentic but expired. A degree can be authentic and permanently valid. A file can be uploaded but authenticity can remain unknown.

## Verification engine

Verification is a first-class platform capability, not a UI label.

```text
verification/
  identity_match
  issuer_match
  document_match
  signature_check
  qr_check
  metadata_check
  registry_check
  historical_record_check
  human_review
```

Verification methods can include:

- Digital issuer or registry API match.
- Digital signature and certificate validation.
- QR or document URI validation.
- Historical registry lookup.
- Human government or issuer review.

AI can assist with OCR, classification, extraction, matching and risk indicators. AI must never make the final government decision. Final authority belongs to the authorised issuer, verifier or government officer.

## Verification levels

| Level | Name | Meaning |
| --- | --- | --- |
| 0 | Uploaded | File is present; trust is not established. |
| 1 | Digitally parsed | OCR and structured fields have been extracted. |
| 2 | Identity matched | Subject identity has been matched to the document claim. |
| 3 | Issuer data matched | Issuer or registry data supports the claim. |
| 4 | Government verified | Authorised verifier confirms the record. |
| 5 | Cryptographically verified | Signature, URI, secure issuer API or equivalent proof confirms the record. |

## Government verification workflow

Citizen-submitted and legacy records can become trusted only through a separate verification case.

```text
Citizen upload
  -> OCR and classification
  -> Claimed issuer detection
  -> Verification route discovery
  -> Automated checks
  -> Government verifier queue
  -> Verify / reject / request evidence / transfer / mark duplicate
  -> Verification result
  -> Wallet trust status
```

Each verification case must retain submitted evidence references, automated match summaries, officer decision metadata, timestamps and an audit trail.

## Correction and versioning

DigiIn must support the citizen problem: "my government record is wrong."

Correction does not overwrite history.

```text
Original document v1
  -> correction request
  -> evidence submission
  -> issuer or verifier review
  -> corrected / rejected
  -> new document version v2
```

Each version records previous version, new version, reason, authority, date, verification result and current status.

## Requester and sharing architecture

Requesters should receive the minimum necessary proof, not always the raw file.

```text
Requester asks for proof
  -> citizen reviews consent
  -> DigiIn resolves document and trust state
  -> requester receives verification result or selected fields
  -> audit event is recorded
```

A requester may need "degree verified, issuer confirmed, status active" rather than the full degree PDF. This protects citizens and reduces unnecessary disclosure.

## Government organisation roles

One government or authorised organisation can act in three roles:

| Role | Responsibility |
| --- | --- |
| Issuer | Creates or exposes official records. |
| Verifier | Confirms citizen-submitted, legacy or disputed records. |
| Requester | Requests proof from citizens with consent. |

The platform should model organisations, departments, offices, issuers, verifiers, requesters, officers, document types and role assignments explicitly.

## Canonical data foundation

Future persistent storage should model these entities:

- `users`, `identities`
- `organizations`, `departments`, `officers`, `roles`
- `issuers`, `verifiers`, `requesters`
- `document_types`, `documents`, `document_versions`, `document_files`
- `document_sources`, `document_provenance`
- `verification_cases`, `verification_methods`, `verification_results`, `verification_evidence`
- `government_records`, `legacy_records`
- `consent_requests`, `consent_grants`, `shares`
- `correction_requests`, `appeals`
- `transactions`, `transaction_steps`, `failure_events`, `recovery_actions`
- `audit_events`

The most important relationships are:

```text
User
  |
  +-- Identity
  |
  +-- Document
        |
        +-- Source
        +-- Versions
        +-- Verification cases
        +-- Consent grants
        +-- Shares
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
| `POST /api/v1/verification/request` | Create a purpose-bound proof request |
| `POST /api/v1/verification/request/demo-exam` | Create a synthetic multi-credential exam request |
| `POST /api/v1/verification/request/{id}/authorize` | Citizen authorises or declines the request |
| `GET /api/v1/verification/request/{id}/status` | Inspect request and verification status |
| `GET /api/v1/verification/result/{id}` | Read a verification result and receipt |
| `GET /api/v1/verification/token/{id}` | Read the signed proof token for a result |
| `POST /api/v1/verification/introspect` | Validate signature, audience, expiry and purpose |

## Implemented verification gateway slice

The current implementation supports the new "proof, not document" pattern with synthetic credentials:

```text
Requester portal
  -> creates verification request
  -> citizen reviews consent
  -> DigiIn evaluates mock credentials
  -> DigiIn returns a signed, short-lived, audience-bound proof token
  -> requester introspects token
  -> citizen receives a receipt
```

Implemented demo credentials include Class XII, domicile, age over 18, graduation and category certificate. The gateway supports boolean and attribute disclosure modes and keeps document retrieval separate from verification.

## Next modules requiring authorised integration

- OIDC/PKCE session identity and device management.
- Persistent PostgreSQL transaction, document, verification and audit storage.
- Production-grade proof signing with managed keys, rotation, replay protection and requester registration.
- Citizen upload processing with malware scanning, OCR and metadata extraction.
- Digital signature, QR, URI, registry and hash verification.
- Government verifier console with queue, evidence review and officer audit.
- Legacy digitization pipeline for historical records.
- Correction, appeal and document versioning workflows.
- Consent grant, revoke and requester proof APIs.
- Issuer/requester/verifier partner sandbox, certification, mTLS and service-level agreements.

These are deliberately not faked. No live government source, identity credential, legal verification, OTP, Aadhaar identifier, or official document file is processed by this prototype.
