# DigiLocker X (DigiIn)

[![CI Pipeline](https://github.com/SahilKhutey/DigiIn/actions/workflows/ci.yml/badge.svg)](https://github.com/SahilKhutey/DigiIn/actions/workflows/ci.yml)
[![Security Audit](https://github.com/SahilKhutey/DigiIn/actions/workflows/security.yml/badge.svg)](https://github.com/SahilKhutey/DigiIn/actions/workflows/security.yml)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Python: 3.11 | 3.12](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![TypeScript: 5.x](https://img.shields.io/badge/TypeScript-5.x-3178C6.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

DigiLocker X is a citizen-centric **credential and verification platform** for Indian public digital services. It enforces sovereign data ownership, minimum disclosure, and zero raw document transfers by exchanging **cryptographically signed verifiable claims** over raw document files:

$$\text{Upload / Request} \longrightarrow \text{OCR \& Extraction} \longrightarrow \text{Issuer Adapter / Gov Review} \longrightarrow \text{Citizen Consent} \longrightarrow \text{Signed Proof} \longrightarrow \text{Proof Introspection}$$

---

## 📖 Authoritative Engineering Specifications (`docs/`)

The single source of truth for the entire platform implementation:

| Specification | Description |
|---|---|
| [**Workflow.md**](docs/Workflow.md) | Platform behavior, citizen journeys, government issuance, OCR pipeline, verification rules, consent-controlled sharing, and cryptographic proof schemas. |
| [**Principles.md**](docs/Principles.md) | The 15 mandatory engineering principles (Citizen First, Verify Don't Copy, Minimum Disclosure, Explicit Consent, Purpose Limitation, Security by Default, Accessibility WCAG 2.2 AA). |
| [**Services.md**](docs/Services.md) | Detailed boundaries and interfaces for all 13 platform services (Identity, Document, Credential, Verification, Consent, Proof, Issuer, Requester, Review, Notification, Audit, Search, Integration). |
| [**CoreFoundation.md**](docs/CoreFoundation.md) | Architectural layout, technology stack (FastAPI, Next.js, React Native, PostgreSQL 16, Redis, S3), and layer isolation rules. |
| [**Database.md**](docs/Database.md) | Entity-relationship models, PostgreSQL DDL schemas, constraints, version chains, and immutable domain events. |
| [**Auth.md**](docs/Auth.md) | Multi-factor passwordless auth (Mobile OTP, Passkeys, eKYC), token architecture (15m JWT, rotating refresh tokens), OAuth 2.0 / OIDC delegation, and RBAC matrix. |
| [**UI-UX.md**](docs/UI-UX.md) | Information architecture, 8 universal UI states, ASCII wireframes for all 23 screens, and WCAG 2.2 AA accessibility guidelines. |

---

## 🏛️ Monorepo Workspace Structure

```text
digilocker-x/
├── docs/                      # The 7 authoritative single-source-of-truth specifications
│   ├── Workflow.md
│   ├── Principles.md
│   ├── Services.md
│   ├── CoreFoundation.md
│   ├── Database.md
│   ├── Auth.md
│   └── UI-UX.md
│
├── apps/                      # Frontends & Consoles
│   ├── web/                   # Citizen web application (React 19 / Next.js / Vite)
│   ├── mobile/                # Citizen mobile app (React Native / Expo)
│   ├── issuer-console/        # Government Issuer portal (CBSE, State Boards)
│   ├── verifier-console/      # Requester verification query portal (NTA, Universities)
│   └── admin/                 # Platform administration & system governance
│
├── services/                  # Backend Modular Services & Workers
│   ├── api/                   # Core FastAPI modular monolith with Issuer Adapters & Proof Engine
│   ├── worker/                # Background async task queue for OCR & virus scanning
│   ├── verification/          # Standalone verification evaluation rules engine
│   └── notification/          # Multi-channel notification dispatcher (SMS, WhatsApp, Push)
│
├── packages/                  # Shared Isomorphic TypeScript Packages
│   ├── ui/                    # Accessible UI components & universal StateContainer
│   ├── types/                 # Shared TypeScript models & domain entities
│   ├── schemas/               # Authoritative JSON Schemas (RFC 7515/7519 Proofs)
│   ├── api-client/            # Isomorphic typed SDK for Web, Mobile, and Consoles
│   └── config/                # Shared TSConfig and linting rules
│
├── infrastructure/            # Production & Local Infrastructure
│   ├── docker-compose.yml     # PostgreSQL 16, Redis, API, and Web containers
│   └── postgres/init.sql      # Database DDL initialization script
│
├── tests/                     # Monorepo Integration & E2E Test Suites
│   ├── test_document_pipeline_e2e.py
│   └── e2e_verification_flow.py
│
└── README.md
```

---

## 🔗 Platform Endpoint Mappings

### 1. eKYC & Identity Verification Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/ekyc/otp/generate` | Generate simulated 6-digit OTP challenge against UIDAI reference |
| `POST` | `/api/v1/ekyc/otp/verify` | Verify OTP, execute demographic matching, and sign eKYC assertion |
| `POST` | `/api/v1/ekyc/match-demographics` | Calculate confidence match score between Aadhaar and document claims |
| `GET` | `/.well-known/jwks.json` | Public RFC 7517 JSON Web Key Set for offline asymmetric verification |

### 2. Document Pipeline & Government Review Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/documents/upload-pipeline` | Secure file upload, SHA-256 integrity hash, OCR entity extraction, and case enqueuing |
| `GET` | `/api/v1/government/queues` | Summary metrics across departmental review queues (CBSE, Revenue, Transport) |
| `GET` | `/api/v1/government/cases` | List pending document discrepancy verification cases |
| `GET` | `/api/v1/government/cases/{id}/comparison` | Side-by-side comparison of citizen OCR claims vs official state registry |
| `POST` | `/api/v1/government/cases/{id}/decision` | Submit officer adjudication (`VERIFY`, `REJECT`, `TRANSFER`), elevating to Level 4 |

### 3. Verification, Consent & Proof Validation Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/verification/requests` | Inbound verification query ingestion by accredited requesting entity |
| `POST` | `/api/v1/verification/requests/{id}/consent` | Citizen authorization with selective disclosure or zero-knowledge mode |
| `POST` | `/api/v1/verification/requests/{id}/run` | Execute adapter verification and generate signed proof token |
| `GET` | `/api/v1/proofs/{id}/verify` | Cryptographically validate proof token signature and payload claims |
| `POST` | `/api/v1/verification/introspect` | Online and offline RFC 7519 proof introspection with audience verification |

---

---

## 🏆 Hackathon Live Demonstration & Presentation

To execute the live interactive 10-step flagship demonstration showcase during presentations or judging:

```powershell
python scripts/hackathon_showcase.py
```

### Demonstration Endpoints (`/api/v1/demo/*` & `/api/v1/ops/*`)

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/demo/run-scenario` | Execute 10-milestone flagship end-to-end hackathon showcase with live telemetry |
| `GET` | `/api/v1/demo/personas` | List pre-configured demonstration personas (Citizen, Officer, Reviewer, Operator) |
| `GET` | `/api/v1/demo/scorecard` | Export live judge evaluation scorecard (architecture, security, SLOs) |
| `POST` | `/api/v1/demo/qr/encode` | Compress & encode verifiable proof into compact URL-safe QR payload |
| `POST` | `/api/v1/demo/qr/decode` | Decompress & validate QR payload for instant offline camera verification |
| `GET` | `/api/v1/ops/dashboard` | Real-time system operations dashboard (health, throughput, queue depth, p95 latency) |
| `GET` | `/api/v1/ops/slo` | Service Level Objectives (SLO) compliance evaluation report |
| `GET` | `/api/v1/ops/dlq` | Dead-Letter Queue (DLQ) inspection & retry management |

---

## 🧪 Automated Testing & CI Execution

### Run Complete Monorepo Test Matrix (41 Suites — 100% Pass)

```powershell
# Run unified test orchestrator across all 41 test suites
python tests/run_all_tests.py
# or via Makefile
make test
```

---

## 🛡️ Sovereign Milestone & Phase Maturity Status

- [x] **Phase 1: Core Foundation Hardening** — Modular layout, layer isolation, 8-stage verification pipeline
- [x] **Phase 2: Core Workflow & State Machines** — Purpose-bound consent, review queues, transactional outbox
- [x] **Phase 3: Security & Anti-Piracy** — Digital watermarks, anti-replay nonces, counterfeit fingerprint registry
- [x] **Phase 4: Multi-Language Localization** — English (`en`) and Hindi (`hi`) parity
- [x] **Phase 5: Background Worker & Pipeline** — Asynchronous OCR, malware scanning, duplicate detection
- [x] **Phase 6: Verification Intelligence** — Cross-evidence fusion, risk scoring, confidence matrix
- [x] **Phase 7: Government & External Integrations** — Isolated adapter contracts, CBSE/Revenue/Transport mocks, Webhook Gateway
- [x] **Phase 8: Security, Privacy & Compliance Hardening** — AES-256-GCM Envelope Encryption, Key Registry, ABAC Policy Engine, SHA-256 Hash Chain Audit, PII minimization
- [x] **Phase 9: Scale, Observability & Production Operations** — Async Job Workers with DLQ, Idempotency Engine, Object Storage with SHA-256 integrity, Three Pillars of Observability, 3-Tier Health Probes, Disaster Recovery Drills (RPO $\le 15$m, RTO $\le 60$m)
- [x] **Phase 10: Public Release & Hackathon Demonstration Layer** — Multi-persona showcase, Verifiable QR packaging, Live Judge Scorecard, Standalone Demonstration CLI

---

## 📄 License

Released under the [MIT License](LICENSE).

