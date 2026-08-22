# DigiIn MVP — Delivery Plan

## Goal

Build a demonstrable recovery layer for a citizen who cannot obtain or share an **issued** document. The prototype must make the failed step, accountable party and next safe action clear.

## Primary user story

> As a citizen trying to use an official document, I want to know why the journey stopped and what I can do now, without revealing credentials or restarting every step.

## MVP journeys

| ID | Scenario | Diagnostic outcome | Success condition |
| --- | --- | --- | --- |
| J1 | Education document identity mismatch | `identity_mismatch` | Citizen sees the data category to check and the issuer’s correction route. |
| J2 | Issuer record unavailable | `issuer_unavailable` | Citizen sees that the issuer, not their account, is unavailable and gets a retry/alternative route. |
| J3 | External portal callback failed | `callback_failed` | Citizen sees that official authentication completed but the requesting portal needs recovery. |
| J4 | Document retrieved successfully | `resolved` | Citizen sees a complete end-to-end evidence timeline. |

## Delivery backlog

### Milestone 1 — Prototype foundation

- [x] Define MVP boundary, privacy baseline and architecture.
- [x] Establish web/API workspace and versioned diagnostic contract.
- [x] Provide a synthetic, runnable diagnostic journey.

### Milestone 2 — Diagnostic experience

- [x] Create a document-intent form: category and trust type (no credentials or identifiers).
- [x] Model identity, issuer, retrieval, consent and callback stages.
- [x] Implement scenario-driven diagnostic responses.
- [x] Add progress, plain-language failure descriptions and accessible status announcements.
- [ ] Add a printable recovery summary that excludes personal information.

### Milestone 3 — Recovery and evidence

- [x] Create an action catalogue: retry, wait, correct issuer data, use an official alternative route and contact requester.
- [x] Define a privacy-minimised support-evidence reference (`journey_id`, opaque correlation ID and outcome).
- [ ] Add a citizen-visible history mock and a support-safe export.
- [ ] Define route ownership and service-level expectations with each participating body.

### Milestone 4 — Production-readiness gates

- [ ] Conduct a threat model, DPIA and consent UX review.
- [ ] Agree authorised API Setu/DigiLocker and issuer integration contracts; do not screen scrape.
- [ ] Add authentication, rate limiting, audit storage, encryption, monitoring and incident runbooks.
- [ ] Test low bandwidth, network changes, session expiry, keyboard navigation, screen readers and Hindi/local-language content.

## API implementation contract

| Endpoint | Purpose | Personal data policy |
| --- | --- | --- |
| `GET /health` | Operational health check | None |
| `GET /api/v1/scenarios` | Lists synthetic prototype cases | None |
| `GET /api/v1/documents?q=` | Searches the mock document catalogue | None |
| `GET /api/v1/documents/{id}` | Returns document-type trust metadata | None |
| `GET /api/v1/transactions/{id}/diagnosis` | Returns a fictional diagnostic timeline | None |
| `POST /api/v1/transactions/{id}/retry` | Runs a mock targeted retry | None |
| `GET /api/v1/issuers/health` | Returns fictional issuer health states | None |
| `GET /api/v1/consents/preview` | Returns a plain-language consent preview | None |

Future production APIs must accept only consented, minimised opaque references. DigiIn must never proxy Aadhaar numbers, OTPs, passwords, security PINs, or full documents.

## Acceptance criteria

1. A person can select each of the four failure/success scenarios and understand the diagnostic without technical terminology.
2. Every non-complete stage identifies who owns the next action.
3. The interface says whether a retry is meaningful and avoids implying that DigiIn can correct official records.
4. No form or log needs a government credential or real document.
5. The web interface works at 320px width and via keyboard.
6. API responses conform to the shared diagnostic schema.

## Success metrics for a future pilot

- End-to-end document success rate.
- Time to a clear next action.
- Repeat attempts per journey.
- Percentage of generic errors converted into classified states.
- Recovery completion by category, issuer and destination (aggregated only).
