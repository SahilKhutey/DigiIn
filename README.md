# DigiLocker X (DigiIn)

[![CI Pipeline](https://github.com/SahilKhutey/DigiIn/actions/workflows/ci.yml/badge.svg)](https://github.com/SahilKhutey/DigiIn/actions/workflows/ci.yml)
[![Security Audit](https://github.com/SahilKhutey/DigiIn/actions/workflows/security.yml/badge.svg)](https://github.com/SahilKhutey/DigiIn/actions/workflows/security.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

DigiLocker X is a citizen-centric **credential and verification platform** for Indian public digital services. It enforces sovereign data ownership, minimum disclosure, and zero raw document transfers by exchanging **cryptographically signed verifiable claims** over raw document files.

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
│   ├── web/                   # Citizen web application (React / Next.js ready)
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
│   └── e2e_verification_flow.py
│
└── README.md
```

---

## 🚀 Quick Start

### 1. Run the Backend API (`services/api`)

```powershell
cd services/api
python -m pytest               # Runs 21 unit & adapter tests
uvicorn app.main:app --reload --port 8000
```
API Documentation is available at `http://localhost:8000/docs`.

### 2. Run the Citizen Web App (`apps/web`)

```powershell
cd apps/web
npm install
npm run dev
```
The citizen web application runs at `http://localhost:5173`.

### 3. Run the End-to-End Verification Test (`tests/`)

Executes the complete vertical slice: `Request Creation` ➔ `Citizen Consent` ➔ `Issuer Verification` ➔ `Signed Proof Generation` ➔ `Proof Introspection`.

```powershell
python tests/e2e_verification_flow.py
```

---

## 🛡️ Core Verification Milestone Status

- [x] **Web Application**: Accessible citizen interface with 8 UI states (`apps/web`)
- [x] **Mobile Shell**: 5-tab React Native / Expo application (`apps/mobile`)
- [x] **Authentication**: Passwordless OTP challenge & rotating refresh tokens (`/api/v1/auth/otp/*`)
- [x] **Document Wallet**: Multi-tier trust badges with Level 0-4 verification (`/api/v1/wallet/documents`)
- [x] **Issuer Adapters**: Standardized `IssuerAdapter` protocol with mock CBSE, State Board & University implementations
- [x] **Verification Request Gateway**: Purpose-bound query ingestion with minimum disclosure configuration
- [x] **Citizen Consent Flow**: Explicit attribute authorization and instant one-click revocation
- [x] **Proof Engine**: Asymmetrically signed JWS/JWT proof generation and public JWKS discovery
- [x] **Requester Introspection**: Third-party offline and online proof validation (`/api/v1/verification/introspect`)
- [x] **Sovereign Audit Trail**: Append-only tamper-evident domain event ledger (`/api/v1/audit/events`)

---

## 📄 License

Released under the [MIT License](LICENSE).
