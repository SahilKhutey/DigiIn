# DigiLocker X — Engineering Principles

These 15 foundational engineering principles govern every architectural, security, and interface decision across the DigiLocker X platform.

---

## 1. Citizen First
The platform exists to eliminate repetitive friction in public digital interactions:
- Reduce repeated file uploads across government portals
- Eliminate unnecessary physical office visits for document verification
- Replace manual document scrutiny with automated cryptographic checks
- Prevent duplicate data submissions
- Remove uncertainty by providing clear real-time diagnostic status and recovery paths

---

## 2. Verify, Don't Copy
Prefer:
```
VERIFIED = TRUE
```
over:
```
Upload PDF / Transfer File
```
Whenever the underlying physical document is not legally mandated by statutory decree, applications must exchange verifiable claims rather than transferring complete document payloads.

---

## 3. Minimum Disclosure
Disclose only the precise subset of attributes required for the stated purpose.

**Example**:
- *Legacy approach*: Requester collects complete Date of Birth (DOB) and Aadhaar PDF copy.
- *DigiLocker X approach*: Requester queries `is_age_over_18`, and receives `TRUE` without learning the exact birth day, month, or year.

---

## 4. Explicit Consent
No credential or personal attribute can be shared without explicit, informed authorization from the citizen, except where a legally defined statutory workflow explicitly requires automated compliance. Every consent transaction must be recorded in an immutable audit ledger.

---

## 5. Purpose Limitation
Every consent transaction and proof token must be bound to a distinct, declared scope:
- **Requester**: The specific registered organization receiving the claim
- **Purpose**: The declared justification (e.g., `EXAM_ADMISSION`, `LOAN_UNDERWRITING`)
- **Credential & Attributes**: The exact fields authorized for release
- **Duration**: Strict time-to-live (TTL), defaulting to single-use or 10–15 minutes

---

## 6. Security by Default
Adopt a zero-trust model at every layer:
- Never trust client-side permissions or client-provided user IDs
- Never expose direct database, object storage, or cache access to clients
- Treat all document URLs as transient, pre-signed, and time-bounded
- Reject unsigned or expired credentials
- Sign all platform proof assertions using HSM-backed or asymmetric keys

---

## 7. Accessibility by Default
The platform must be universally usable by all citizens:
- Full keyboard navigation and visible focus management
- Screen reader accessibility conforming to **WCAG 2.2 AA**
- High-contrast color palettes and scalable typography
- Initial bilingual support for **Hindi and English**, with modular localization architectures for all scheduled Indian languages
- Resilient operation in low-bandwidth, high-latency network environments

---

## 8. Mobile + Web Parity
Business logic, verification engines, and cryptographic validation must reside exclusively in backend services. Both the Web client and the Mobile application are client rendering targets consuming the identical versioned API contracts.

---

## 9. API First
All platform capabilities must be exposed via well-documented, versioned REST / JSON-RPC APIs:
```
/api/v1/...
```
No private backdoor channels or undocumented couplings are permitted between applications and domain services.

---

## 10. Modular Architecture
Start as a clean, highly cohesive **modular monolith** with strict domain boundaries (`identity`, `documents`, `credentials`, `verification`, `consent`, `audit`). Sub-services can be extracted independently into microservices or serverless functions as scale demands without breaking domain abstractions.

---

## 11. Configuration over Hard Coding
Government credential schemas, verification rule sets, OCR template geometries, and issuer adapter configurations must be stored as declarative JSON/YAML schemas, allowing runtime evolution without code redeployments.

---

## 12. Failure Is a State
Do not hide failures behind generic error alerts. Every failure must have:
- Standardized machine-readable error codes (`ISSUER_UNAVAILABLE`, `IDENTITY_MISMATCH`, `NOT_FOUND`)
- Human-readable plain-language explanations
- Configured retry policies (exponential backoff)
- Explicit recovery action paths for citizen assistance

---

## 13. Audit Everything Important
Maintain an append-only, tamper-evident audit trail for:
- Authentication events and device registrations
- Consent grants, modifications, and revocations
- Verification requests and issuer queries
- Document uploads, version updates, and officer review decisions

*Crucial Guardrail*: Never log raw sensitive document payloads, PII, passwords, or OTP secrets in logs or audit events.

---

## 14. No Dark Patterns
Respect citizen agency at all times:
- Declining a verification or consent request must be as visible, intuitive, and frictionless as accepting it
- Clearly state what data will be shared before consent is granted
- Provide instant one-click revocation for ongoing consent grants

---

## 15. Data Ownership & Provenance
The platform maintains strict cryptographic and metadata lineage for all data entities:
- **Origin**: Authoritative issuer ID and digital signature
- **Verification Level**: Level 0 (Self-uploaded), Level 2 (OCR Scanned), Level 3 (Officer Verified), Level 4 (Government Source Verified)
- **Version History**: Immutable lineage of corrections and supersessions
- **Access Logs**: Complete history of every requester who has inspected or verified the record
