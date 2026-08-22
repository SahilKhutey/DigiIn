# DigiIn Web System Principles

## Platform principles

1. **Lifecycle before locker.** DigiIn manages the journey of a document across issue, upload, verification, correction, versioning, sharing and recovery.
2. **Provenance before presentation.** A polished PDF is not proof. The platform must know where the document came from and how it was verified.
3. **Trust is multi-dimensional.** Source, authenticity, validity, verification level and current status must remain separate.
4. **Citizen control is mandatory.** Sharing requires informed consent, clear scope and revocation paths.
5. **Minimum disclosure by default.** Share verification results or selected claims when the raw document is not necessary.
6. **Government authority remains authoritative.** AI and automation can assist, but cannot make final government verification, correction or rejection decisions.
7. **Uploaded is not official.** Citizen-uploaded files must be visually and semantically distinct from government-issued or government-verified records.
8. **History is never destroyed.** Corrections and reissues create new versions while preserving provenance and audit history.
9. **Legacy records are first-class.** Old paper records deserve explicit digitization, archival search and human verification workflows.
10. **Failures should be explainable.** Every failed step should name the cause, accountable role, safe next action and support reference.

## Web experience principles

1. **Start from citizen intent.** Ask what the person needs to prove or recover before asking them to navigate departments.
2. **Show trust plainly.** Use labels such as Government issued, Government verified, Uploaded, Pending, Rejected and Unavailable.
3. **Separate file actions from trust actions.** Uploading, viewing, verifying, correcting and sharing are different tasks.
4. **Make verification routes visible.** Show whether a document can be verified automatically, by issuer, by registry, by QR/signature, or by human review.
5. **Never imply unavailable authority.** If an integration or verification route is not authorised, say so and provide a safe fallback.
6. **Design for low confidence states.** Unknown, pending, needs evidence and record not found states are normal product states.
7. **Keep recovery calm and specific.** A citizen should know whether to retry, wait, correct issuer data, submit evidence, contact a requester, or use an official route.
8. **Make support evidence privacy-safe.** Complaint or help references should use opaque IDs and stage outcomes, not personal identifiers.

## Data principles

1. **Separate document, file and verification result.** Verification creates a result object; it does not rewrite the document silently.
2. **Separate citizen upload and government record.** A user file can be linked to, but must not overwrite, an authoritative government record.
3. **Use opaque identifiers.** Document IDs, subject IDs, verification IDs and transaction IDs must avoid exposing sensitive data.
4. **Audit every authority decision.** Verification, rejection, correction, transfer, appeal and revocation decisions require tamper-evident event history.
5. **Retain evidence by reference.** Store only what is necessary, protect evidence strongly, and expose minimal summaries to requesters.
