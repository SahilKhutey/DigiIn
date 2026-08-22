# Website workflow and feature implementation

## Citizen journey

```text
Start recovery
  → Select what document is needed (not a department)
  → Choose why it is needed (personal access / share with a service)
  → Check availability and document trust type
  → Inspect live transaction stages
  → Receive a classified outcome
  → Retry only the failed stage, use an official fallback, or create support evidence
```

## Screens and behaviours

| Screen | User task | Implemented behaviour | Privacy rule |
| --- | --- | --- | --- |
| Recovery start | State a document need | Intent-first document picker | No Aadhaar, OTP, password, document number or upload. |
| Document health | Understand document status | Trust label, availability and issuer-health state | Uses synthetic metadata only. |
| Journey diagnosis | Identify the failure | Stage-by-stage state, owner, cause and recovery action | No provider credentials shown or retained. |
| Recovery action | Continue safely | Targeted retry guidance or official alternative route | No automatic retry against a real government system. |
| Support evidence | Ask for help | Creates a minimised, copyable diagnostic reference | Contains only opaque journey ID and stage states. |

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
| User uploaded | A citizen-provided file; it must not be presented as issuer-verified. |
| Pending verification | The system has not received a verifiable issuer result. |

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

## Production integration boundary

Only an authorised, consented integration may replace prototype data. Every adapter must have a documented data contract, timeout policy, user-safe error mapping, observability correlation ID, retention policy and fallback route. Screen scraping and credential proxying are prohibited.
