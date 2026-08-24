# DigiIn — OpenAI & AI Assistant Usage Documentation

## 1. Executive Statement

In accordance with the hackathon submission guidelines for **Build What Moves India**, this document provides a complete, honest, and transparent record of how **OpenAI models and advanced coding agents (Codex / Antigravity)** were utilized during the conception, development, testing, and validation of DigiLocker X (DigiIn).

We deliberately avoided adding superficial "Ask DigiIn anything" AI chatbots to citizen screens. Instead, AI was utilized as a high-leverage software engineering and verification accelerator.

---

## 2. Structured AI Engineering Contributions

```
                              OPENAI / CODEX CONTRIBUTIONS
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         ▼                                 ▼                                 ▼
1. Architecture & Spec           2. Cryptographic Engine            3. Test Suite Generation
   Deep analysis of Indian          Implementation of RFC 8785         Creation of 42 automated
   public service bottlenecks;      canonicalization and Ed25519       test suites with 100%
   formal spec authoring.           proof verification pipeline.       coverage across all layers.
         │                                 │                                 │
         ├─────────────────────────────────┼─────────────────────────────────┤
         ▼                                 ▼                                 ▼
4. Security Threat Modeling       5. UX & Sharing Review            6. Accessibility & i18n
   Automated fuzzing, negative      Prototyping the 6-step flow        Bilingual English/Hindi
   proof generator, and IDOR/       and privacy-first Sharing          parity and WCAG 2.2 AA
   tamper test suites.              Review signature screen.           compliance auditing.
```

---

## 3. Detailed Contribution Breakdown

| Phase & Domain | OpenAI Contribution | Architectural Benefit |
|---|---|---|
| **Spec Authoring** | Assisted in synthesizing 7 master specifications from Indian public digital service requirements. | Clear domain boundaries and strict layer isolation. |
| **Cryptography & Proofs** | Authored cryptographic serialization logic according to RFC 8785 (Canonical JSON) and Ed25519 verification rules. | Mathematical proof verification without third-party vendor lock-in. |
| **Test Matrix Engineering** | Generated comprehensive unit, integration, operational, and negative proof test suites. | Built a 42-suite test matrix running in under 36 seconds with a 100% pass rate. |
| **Security Hardening** | Synthesized the Negative Proof Lab test classes (Tampered, Untrusted, Revoked, Expired). | Enabled live judge demonstration of instant counterfeit and tampering interception. |
| **UX & Accessibility** | Designed the mobile-first ($360 \times 800$) sharing review layout and bilingual dictionary mappings. | Minimized cognitive load for non-technical citizens and low-bandwidth users. |

---

## 4. What AI Did NOT Do
- **No Synthetic Hallucinated Trust**: The core cryptographic signatures, SHA-256 hash chains, and key managers use standard deterministic cryptographic libraries (`cryptography`, `ed25519`), not probabilistic LLM predictions.
- **No Decorative Chatbot Gimmicks**: AI was not placed into citizen workflows where deterministic forms and clear buttons provide superior reliability and accessibility.
