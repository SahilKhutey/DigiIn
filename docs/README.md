# DigiLocker X — Engineering Documentation

This directory defines the **single source of truth** for the DigiLocker X engineering implementation, governance, architecture, and interfaces.

---

## 📖 Core Engineering Specifications (Single Source of Truth)

| # | Specification | Focus Area | Description |
|:---:|---|---|---|
| **01** | [**Workflow.md**](Workflow.md) | Platform Behavior & Workflows | Actors, citizen dashboard journeys, government issuance, self-upload OCR pipeline, verification rules, consent-controlled sharing, and cryptographic proof schemas. |
| **02** | [**Principles.md**](Principles.md) | Engineering Principles | The 15 mandatory engineering principles: Citizen First, Verify Don't Copy, Minimum Disclosure, Explicit Consent, Purpose Limitation, Security by Default, Accessibility (WCAG 2.2 AA), and Parity. |
| **03** | [**Services.md**](Services.md) | Service Specifications | Detailed responsibilities, domain boundaries, inputs, and outputs for all 13 platform services (Identity, Document, Credential, Verification, Consent, Proof, Issuer, Requester, Review, Notification, Audit, Search, Integration). |
| **04** | [**CoreFoundation.md**](CoreFoundation.md) | Backend Architecture & Tech Stack | Gateway, modular monolith organization, technology stack (Python/FastAPI, Next.js/React, React Native/Expo, PostgreSQL 16, Redis, S3), and strict zero-trust boundary rules. |
| **05** | [**Database.md**](Database.md) | Data Models & Schemas | Entity-relationship models, PostgreSQL DDL schemas, foreign keys, indexes, version chains, domain events, and audit ledgers. |
| **06** | [**Auth.md**](Auth.md) | Authentication & Security | Passwordless auth (Mobile OTP, Passkeys, eKYC), token architecture (15m JWT, rotating refresh tokens), OAuth 2.0 / OIDC delegation, RBAC permissions matrix, and throttling. |
| **07** | [**UI-UX.md**](UI-UX.md) | Screen Specs & Design System | Route map, universal 8 UI states (`LOADING`, `EMPTY`, `SUCCESS`, `ERROR`, `PENDING`, `OFFLINE`, `UNAUTHORIZED`, `EXPIRED`), ASCII screen wireframes, and WCAG 2.2 AA accessibility guidelines. |

---

## 📚 Supporting Architectural Reference Documents

- [**Task List & Status**](Task-List.md): Comprehensive implementation checklist across all 13 platform services and 11 testing suites.
- [**Foundation Architecture**](foundation-architecture.md): Deep-dive into modular-monolith boundaries and local execution paths.
- [**Product Scope**](product-scope.md): Scope boundaries and synthetic verification testing fixtures.
- [**Security Baseline**](security.md): Cryptographic security, data minimization, and HSM key rotation policies.

