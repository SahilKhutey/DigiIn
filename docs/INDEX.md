# DigiLocker X (DigiIn) — Master Documentation Index

Welcome to the authoritative documentation suite for **DigiLocker X (DigiIn)** — a sovereign Digital Trust & Verification Infrastructure built for the *Build What Moves India* Hackathon.

---

## 🏛️ 1. Architecture & Technical Specifications

| Document | Description | Key Focus Areas |
|---|---|---|
| 📐 [**Master Architecture Specification**](./architecture/MASTER_ARCHITECTURE.md) | Platform reference architecture and core system design | 6-Layer Architecture, Core Invariants, ABAC & ZK rules |
| 🗂️ [**Repository Structure & Subsystems Catalog**](./architecture/REPOSITORY_STRUCTURE.md) | Complete directory tree and module breakdowns | Apps, Services, Crypto, Async Worker, DB Models |
| 📊 [**System Flowcharts & Visual Architecture**](./architecture/SYSTEM_FLOWCHARTS.md) | Visual Mermaid diagrams of all end-to-end flows | Flagship Flow, Async Pipeline, Tamper Defense, Hash Chain |
| 🧪 [**Test Cases & Verification Matrix**](./architecture/TEST_CASES_AND_VERIFICATION_MATRIX.md) | Complete automated test coverage and proof classes | 44 Test Suites, 12 Builder Brief Gates, Negative Proof Lab |

---

## 🏆 2. Hackathon Evaluation & Submission Suite

| Document | Description | Key Topics |
|---|---|---|
| 📋 [**Hackathon Master Index**](./hackathon/README.md) | Central entry point for hackathon judges & reviewers | Problem overview, flagship metrics, quickstart |
| 🚨 [**Problem Statement & Inefficiencies**](./hackathon/PROBLEM.md) | The national crisis of document re-uploads & PII leaks | Traditional vs DigiIn comparative metrics |
| 🎓 [**Flagship 7-Screen Scholarship Journey**](./hackathon/FLAGSHIP_JOURNEY.md) | Step-by-step flagship user flow walkthrough | Zero raw document uploads, 2-minute completion |
| 🔒 [**Privacy & Anti-Leakage Architecture**](./hackathon/PRIVACY.md) | Minimal disclosure, ZK predicates & data boundary | Zero raw PII retention, strict request whitelisting |
| 🛡️ [**Cryptographic Verification & Negative Proofs**](./hackathon/VERIFICATION.md) | Ed25519 signatures, RFC 8785 digests & tamper defense | Live tamper demo, revocation check, expiry check |
| ♿ [**Accessibility & Data Saver Mode**](./hackathon/ACCESSIBILITY_AND_DATA_SAVER.md) | UX4G 3.0, WCAG 2.2 AA, low-bandwidth mode | 93.5% bandwidth reduction, English/Hindi parity |
| 🎬 [**3-Minute Live Jury Walkthrough Script**](./hackathon/DEMO_SCRIPT.md) | Minute-by-minute live judging script | 1-Click Persona, Consent Review, Tamper Defense |
| 📜 [**Phase 39 Browser Demo Certification**](./hackathon/PHASE_39_BROWSER_DEMO_CERTIFICATION.md) | Phase 39 Web Launch & Browser QA Sign-Off | 14 Browser Acceptance Specs, Playwright Suites |
| 🏅 [**Final Release Verification Report**](./hackathon/FINAL_RELEASE_VERIFICATION_REPORT.md) | Official Release Candidate certification report | Monorepo matrix sign-off, build metrics |

---

## 🚀 3. Cloud Deployment & Operational Guides

| Document | Description | Highlights |
|---|---|---|
| 🌐 [**Cloud Deployment Guide (DEPLOYMENT.md)**](../DEPLOYMENT.md) | Complete production & sandbox deployment guide | Render Blueprint, environment variables, health checks |
| ⚙️ [**Render Blueprint (render.yaml)**](../render.yaml) | 1-Click Render Cloud infrastructure specification | `digiin-web`, `digiin-api`, `digiin-worker`, `digiin-db` |
| 📖 [**Main Project Readme**](../README.md) | Main repository introduction & quickstart | Local development commands, system architecture |

---

## 🧪 4. Browser Acceptance Test Specifications (`tests/browser/`)

- [01: Home Page & Public Experience](../tests/browser/01-home.md)
- [02: Public Services Discovery Catalog](../tests/browser/02-services.md)
- [03: 1-Click Demo Persona Authentication](../tests/browser/03-citizen-login.md)
- [04: Flagship Scholarship Happy Path](../tests/browser/04-scholarship-happy-path.md)
- [05: Consent Denial & Zero Disclosure](../tests/browser/05-consent-denied.md)
- [06: Tampered Claim Rejection Demo](../tests/browser/06-tampered-proof.md)
- [07: Expired Proof Token Rejection](../tests/browser/07-expired-proof.md)
- [08: Revoked Credential Rejection](../tests/browser/08-revoked-proof.md)
- [09: Government Issuer Review Workflow](../tests/browser/09-issuer-workflow.md)
- [10: Institutional Verifier Portal](../tests/browser/10-verifier-workflow.md)
- [11: Administrator & Sovereign Audit Chain](../tests/browser/11-admin-workflow.md)
- [12: English / Hindi Bilingual Parity](../tests/browser/12-hindi.md)
- [13: Multi-Device Responsive Layouts](../tests/browser/13-responsive.md)
- [14: 1-Click Demo Sandbox Reset](../tests/browser/14-demo-reset.md)
