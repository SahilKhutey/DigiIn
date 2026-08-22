# Website workflow and feature implementation

## Product posture

The web system should present DigiIn as a document lifecycle and trust platform. Recovery is the first implemented workflow, but the long-term experience must also support issuing, upload, verification, legacy digitization, correction, versioning, consented sharing and requester proof.

## Citizen journey

```text
Document center
  -> choose need: receive / upload / verify / correct / share / recover
  -> select document type or proof goal
  -> review source and trust state
  -> follow the correct lifecycle workflow
  -> receive verification, recovery, correction or sharing outcome
```

## Primary workflows

| Workflow | Citizen intent | Platform response | Current status |
| --- | --- | --- | --- |
| Recover issued document | "My official document is not available or shareable." | Diagnose identity, issuer, fetch, consent and callback stages. | Implemented with mock scenarios. |
| Upload citizen document | "I have a digital copy or scan." | Store as citizen-uploaded and mark authenticity as not established. | Future module. |
| Verify uploaded document | "Make this old or uploaded document trusted." | Create a verification case, route to issuer/registry/human review and produce a verification result. | Future module. |
| Digitize legacy record | "This record exists only on paper or in archives." | OCR, classify, identify authority, match archive and submit for government review. | Future module. |
| Correct official record | "The government record has an error." | Create a correction case with evidence and issue a new version if approved. | Future module. |
| Share proof | "I need to prove something to a requester." | Share minimum necessary verification result or selected fields with consent. | Future module. |

## Screens and behaviours

| Screen | User task | Implemented behaviour | Privacy rule |
| --- | --- | --- | --- |
| Document center | Choose the lifecycle action | Recovery-first prototype with document picker | No Aadhaar, OTP, password, document number or upload. |
| Document health | Understand document status | Trust label, availability and issuer-health state | Uses synthetic metadata only. |
| Journey diagnosis | Identify the failure | Stage-by-stage state, owner, cause and recovery action | No provider credentials shown or retained. |
| Recovery action | Continue safely | Targeted retry guidance or official alternative route | No automatic retry against a real government system. |
| Support evidence | Ask for help | Creates a minimised, copyable diagnostic reference | Contains only opaque journey ID and stage states. |
| Verification case | Submit evidence for authority review | Not implemented | Must separate AI recommendations from officer decisions. |
| Correction case | Request a corrected or reissued version | Not implemented | Must preserve prior versions and evidence references. |
| Share proof | Share claim or verification result | Not implemented | Must minimise disclosure and require consent. |

## State model

| State | Meaning | Primary CTA |
| --- | --- | --- |
| `complete` | This stage completed | Continue / view evidence |
| `attention` | A user or partner action is needed | Follow the targeted action |
| `blocked` | A dependency is unavailable | Wait, retry later, or use official fallback |
| `not_started` | A preceding stage prevents it | Resolve the earlier stage |

## Trust labels

| Label | Meaning |
| --- | --- |
| Government issued | An authorised issuer is represented as the source in the transaction. |
| Government verified | A citizen-uploaded or legacy record has been verified by an authorised body. |
| Issuer verification | Issuer or registry evidence supports the record, but legal scope may be limited. |
| Citizen uploaded | A citizen-provided file; it must not be presented as issuer-verified. |
| Pending verification | The system has not received a final authorised verification result. |
| Verification rejected | Submitted evidence did not pass verification. |
| Verification unavailable | No authorised verification route is currently available. |

## Document card model

Every document card should show separate signals:

| Signal | Example |
| --- | --- |
| Source | Government issued, citizen upload, legacy scan |
| Authenticity | Verified, unknown, rejected |
| Current status | Active, expired, revoked, superseded |
| Verification level | Uploaded, parsed, identity matched, issuer matched, government verified, cryptographically verified |
| Version | Original, corrected, reissued |

## Feature-to-fix mapping

| Proposed fix | DigiIn prototype implementation |
| --- | --- |
| Smart Document Fetch | Document-first picker, rather than department-first navigation. |
| Explainable Failure Engine | Each failure identifies what happened, responsible party and safe next action. |
| Issuer/API Health Detection | `issuerStatus` on every diagnostic response. |
| Identity Mismatch Resolver | Identity mismatch is explicit, field category is named, and the remedy belongs to the issuer. |
| Transaction Continuity | Callback failure shows that authentication succeeded and names the destination owner. |
| Official Fallback Engine | Each blocked journey offers an official-route recommendation placeholder, pending authorised configuration. |
| Transaction-linked Complaint | A support evidence reference links the exact journey and fault code without personal data. |
| Trust labels | Every example clearly states its verification category. |
| Bring Your Document | Future upload-to-verification flow for old and citizen-held records. |
| My Record Is Wrong | Future correction and versioning flow controlled by the responsible authority. |
| Prove Without Oversharing | Future requester flow returns verification results or selected claims, not always raw files. |

## Production integration boundary

Only an authorised, consented integration may replace prototype data. Every adapter must have a documented data contract, timeout policy, user-safe error mapping, observability correlation ID, retention policy and fallback route. Screen scraping and credential proxying are prohibited.
