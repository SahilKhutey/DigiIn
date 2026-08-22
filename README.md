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

## 🧪 Automated Testing & CI Execution

### 1. Run Complete Monorepo Test Suite (7 Layers)

```powershell
# Run unified test orchestrator (Ruff + Pytest + Consoles + Worker + Pipeline E2E + Core E2E + Offline CLI)
python tests/run_all_tests.py
# or via Makefile
make test
```

### 2. Standalone Backend Pytest Suite & Linter (`services/api`)

```powershell
cd services/api

# Run Ruff linter
python -m ruff check app/ tests/

# Run complete pytest test suite (22 tests)
python -m pytest -v --tb=short
```

### 3. Offline Cryptographic Proof Verifier CLI (`tests/`)

Allows third parties to verify JWS proof tokens offline without server dependencies:

```powershell
# Run sample Ed25519 token generation & mathematical verification
python tests/cli_proof_verifier.py --demo

# Inspect public RFC 7517 JWKS discovery keys
python tests/cli_proof_verifier.py --jwks
```

### 4. Run Frontend Web Application & Build (`apps/web`)

```powershell
cd apps/web

# Install dependencies & run development server
npm install
npm run dev

# Run TypeScript typecheck & production bundle build
npm run build
```


---

## 🛡️ Core Verification Milestone Status

See [**docs/Task-List.md**](docs/Task-List.md) for the complete engineering task matrix.

- [x] **Web Application**: Accessible citizen interface with 8 universal UI states (`apps/web`)
- [x] **Government Issuer Console**: Departmental queues, OCR diff inspection & 1-click credential issuance (`apps/issuer-console`)
- [x] **Requester Console**: Zero-Knowledge query builder & cryptographic JWS token introspector (`apps/verifier-console`)
- [x] **Admin Console**: Sovereign audit stream, telemetry & public JWKS discovery (`apps/admin`)
- [x] **Mobile Shell**: 5-tab React Native / Expo application (`apps/mobile`)
- [x] **Multi-Language Modes**: Interactive English (`en`) & Hindi (`hi`) localization (`packages/i18n`)
- [x] **Authentication**: Passwordless OTP challenges, JWT access tokens & rotating refresh sessions (`/api/v1/auth/*`)
- [x] **eKYC Integration**: Aadhaar OTP verification, demographic matching algorithm, and Ed25519 signed assertions (`/api/v1/ekyc/*`)
- [x] **Document Pipeline**: Secure upload, MIME validation, SHA-256 hashing, and OCR entity extraction
- [x] **Security & Anti-Piracy**: Cryptographic watermarking, anti-replay nonces, counterfeit fingerprint registry & rate limiting
- [x] **Latency & Telemetry**: Microsecond execution profiling with W3C `Server-Timing` and `X-Response-Time`
- [x] **Document Wallet**: Multi-tier trust badges with Level 0-4 verification (`/api/v1/wallet/documents`)
- [x] **Issuer Adapters**: Standardized `IssuerAdapter` protocol with CBSE, State Board & University implementations
- [x] **Verification Request Gateway**: Purpose-bound query ingestion with minimum disclosure configuration
- [x] **Citizen Consent Flow**: Explicit attribute authorization and instant one-click revocation
- [x] **Proof Engine**: Asymmetrically signed JWS/JWT proof generation and public JWKS discovery (`/.well-known/jwks.json`)
- [x] **Requester Introspection**: Third-party offline and online proof validation (`/api/v1/verification/introspect`)
- [x] **Sovereign Audit Ledger**: Block-chained tamper-evident domain event ledger with SHA-256 hash chaining (`services/audit`)
- [x] **Document Catalogue**: Dynamic credential schemas with ZK operator bindings (`services/catalogue`)
- [x] **Automated CI/CD**: 11-suite monorepo test orchestrator (`tests/run_all_tests.py` / `make test`)

---

## 📄 License

Released under the [MIT License](LICENSE).

