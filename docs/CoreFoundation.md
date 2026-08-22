# DigiLocker X — Core Foundation Architecture

This document defines the backend infrastructure, technological stack, architectural boundaries, and code organization rules for the DigiLocker X platform.

---

## 1. System Architecture

```
                    ┌────────────────────────────────────────────────────────┐
                    │                      Client Layer                      │
                    │  Next.js Web │ React Native Mobile │ Consoles (Admin)  │
                    └───────────────────────────┬────────────────────────────┘
                                                │ HTTPS / WSS / REST
                                                ▼
                    ┌────────────────────────────────────────────────────────┐
                    │                      API Gateway                       │
                    │      Rate Limiter • TLS Termination • Auth Guard       │
                    └───────────────────────────┬────────────────────────────┘
                                                │
                                                ▼
                    ┌────────────────────────────────────────────────────────┐
                    │                    Application Core                    │
                    │    ┌──────────────────┬──────────────────┐             │
                    │    │ Identity Service │ Document Service │             │
                    │    ├──────────────────┼──────────────────┤             │
                    │    │ Credential Svc   │ Verification Svc │             │
                    │    ├──────────────────┼──────────────────┤             │
                    │    │ Consent Service  │ Proof Engine     │             │
                    │    └──────────────────┴──────────────────┘             │
                    └───────────────────────────┬────────────────────────────┘
                                                │
                 ┌──────────────────────────────┼──────────────────────────────┐
                 ▼                              ▼                              ▼
    ┌────────────────────────┐    ┌────────────────────────┐    ┌────────────────────────┐
    │     Data & Storage     │    │   Async Task Workers   │    │  Integration Adapters  │
    │  PostgreSQL 16 (Rel.)  │    │  Celery / Redis Queue  │    │  CBSE / State Boards   │
    │  Redis 7 (Cache/Lock)  │    │  OCR & Virus Scanning  │    │  UIDAI eKYC Gateway    │
    │  S3 / MinIO (Blob)     │    │  Webhook Notifications │    │  University Registries │
    └────────────────────────┘    └────────────────────────┘    └────────────────────────┘
```

---

## 2. Technology Stack

### Frontend & Client Applications
- **Web Application**: Next.js 14+ / React 18+, TypeScript, Tailwind CSS, TanStack Query, Zod.
- **Mobile Application**: React Native, Expo, TypeScript, React Navigation.
- **Consoles (Issuer, Verifier, Admin)**: Vite / React / Next.js with shared design system components.

### Backend & Core Services
- **Framework**: Python 3.12+, FastAPI, Pydantic v2 (strict type enforcement and high performance).
- **ORM & Database Access**: SQLAlchemy 2.0 (Async Core & ORM) with Alembic migration engine.
- **Cryptographic Engine**: `cryptography`, `PyJWT`, `authlib` (supporting Ed25519, RSA-PSS, and ES256).

### Data Persistence & Caching
- **Primary Database**: PostgreSQL 16 (Relational, JSONB, indexing, strict constraints).
- **Local Dev / Edge DB**: SQLite (with unified SQLAlchemy schema parity for frictionless testing).
- **Caching & Ephemeral Locks**: Redis 7 (Session revocation lists, OTP challenges, rate limit buckets).
- **Object Storage**: S3-compatible Object Storage (MinIO for local dev, AWS S3 / sovereign storage in production).

### Background Workers & Queue
- **Task Runner**: Celery / Redis Task Queue with async job dispatch.
- **OCR Engine**: Tesseract OCR / EasyOCR document classification wrappers.
- **Virus & Malware Scanning**: ClamAV daemon integration.

---

## 3. Core Architectural Rules

### 1. Strict Layer Isolation
The frontend applications (`apps/web`, `apps/mobile`) **never** directly connect to:
- PostgreSQL / Database
- Redis / Caching layer
- S3 / Object storage bucket directly
- External government APIs / Issuer databases

Every interaction is strictly authenticated and proxied through the versioned backend API gateway (`/api/v1/...`).

### 2. Derived Identity Invariant
Every mutating request derives the authenticated user identity strictly from the cryptographically verified JWT session or token. The backend **never** trusts client-supplied user IDs (e.g., query params or JSON body `user_id`).

### 3. Layered Code Organization
Inside the backend service (`services/api`), code strictly flows in one direction:

$$\text{Router / Endpoint} \longrightarrow \text{Domain Service} \longrightarrow \text{Repository Layer} \longrightarrow \text{Database Model}$$

```
services/api/
├── app/
│   ├── main.py                     # Application entry point & middleware wiring
│   ├── api/
│   │   └── v1/                     # HTTP Route handlers & schema parsing
│   │       ├── auth.py
│   │       ├── documents.py
│   │       ├── credentials.py
│   │       ├── verification.py
│   │       ├── consent.py
│   │       ├── proof.py
│   │       └── users.py
│   ├── domain/                     # Pure domain logic, entities, and protocols
│   │   ├── identity/
│   │   ├── documents/
│   │   ├── credentials/
│   │   ├── verification/
│   │   └── consent/
│   ├── repositories/               # Data access layer & query abstractions
│   │   ├── user_repository.py
│   │   ├── document_repository.py
│   │   └── verification_repository.py
│   ├── integrations/               # External issuer and sovereign system adapters
│   │   ├── base.py                 # IssuerAdapter protocol
│   │   ├── cbse_adapter.py
│   │   ├── university_adapter.py
│   │   └── ekyc_gateway.py
│   ├── db/                         # SQLAlchemy session, engine, and ORM tables
│   │   ├── session.py
│   │   └── models.py
│   └── core/                       # Security, cryptographic keys, settings, logging
│       ├── config.py
│       ├── security.py
│       └── crypto.py
└── tests/                          # Pytest unit, integration, and security suites
```
