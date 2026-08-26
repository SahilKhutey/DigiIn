# DigiLocker X (DigiIn) — Repository Structure & Subsystems Catalog

## 1. Directory Tree Overview

```
DigiIn/
├── apps/                               # Frontend User Interfaces
│   └── web/                            # React 18 + Vite + TypeScript + Tailwind CSS
│       ├── src/
│       │   ├── api/                    # API client bindings (/api/v1/*)
│       │   ├── components/             # Reusable UI & subsystem components
│       │   │   ├── consent/            # Citizen sovereign consent manager
│       │   │   ├── correction/         # Lineage correction & dispute UI
│       │   │   ├── diagnostic/         # System diagnostic & timeline tools
│       │   │   ├── platform/           # Test runner & developer console
│       │   │   ├── scanner/            # Offline QR / cryptographic scanner
│       │   │   ├── ui/                 # UX4G 3.0 atomic design components (Button, Card, Badge, Alert)
│       │   │   ├── verification/       # Direct verification flow & proof gateway
│       │   │   ├── verifier/           # Relying party / verifier console
│       │   │   └── wallet/             # Citizen document center & vault
│       │   ├── context/                # Global React Contexts (Auth, Language, Theme)
│       │   ├── features/               # Route-level feature views
│       │   │   ├── auth/               # 1-Click Persona Sign-In, OTP, Onboarding
│       │   │   ├── demo-lab/           # Negative Proof Lab & Demo Control Center
│       │   │   ├── landing/            # Public homepage & hero presentation
│       │   │   ├── public/             # Informational pages (About, Security, Help, Privacy)
│       │   │   ├── scholarship/        # Flagship 7-Screen zero-upload journey
│       │   │   ├── services/           # Public Services Directory & Discovery Catalog
│       │   │   ├── settings/           # Data Saver Mode & preferences
│       │   │   └── verification/       # CBSE academic 8-step verification flow
│       │   ├── layouts/                # AppShell, GovHeader, Footer (UX4G 3.0 compliant)
│       │   ├── patterns/               # FormPage, Wizard & Dashboard patterns
│       │   ├── services/               # Frontend domain services (auth, mockAuth, wallet)
│       │   └── types/                  # Shared TypeScript interfaces & types
│       ├── e2e/                        # Playwright End-to-End Test Matrix
│       │   ├── 01-wallet-and-trust-signals.spec.ts
│       │   ├── 02-ocr-upload-pipeline.spec.ts
│       │   ├── 03-verifier-console.spec.ts
│       │   ├── 04-correction-lineage.spec.ts
│       │   ├── 05-selective-disclosure-and-zk.spec.ts
│       │   ├── 06-consent-and-revocation.spec.ts
│       │   ├── 07-printable-support-sheet.spec.ts
│       │   ├── 08-offline-qr-verifier.spec.ts
│       │   ├── 09-ekyc-gateway.spec.ts
│       │   ├── 10-builder-brief-flagship.spec.ts
│       │   └── 11-judge-demo-flagship.spec.ts
│       ├── package.json
│       └── Dockerfile
│
├── services/                           # Backend Application & Core Domain Engines
│   └── api/                            # Python 3.12 + FastAPI + SQLAlchemy
│       ├── app/
│       │   ├── api/v1/                 # REST API Routers
│       │   │   ├── auth.py             # Citizen session & token issuing
│       │   │   ├── documents.py        # Citizen document lifecycle & storage
│       │   │   ├── ekyc.py             # Simulated demographic matching & OTP
│       │   │   ├── jobs.py             # Asynchronous processing queue & DLQ
│       │   │   ├── public_service.py   # Flagship scholarship, demo reset & lab
│       │   │   └── verification.py     # Ed25519 proof generation & verification
│       │   ├── core/                   # Domain Logic & Cryptographic Engines
│       │   │   ├── crypto/             # Ed25519, RFC 8785 canonicalizer, AES-256-GCM
│       │   │   ├── abac/               # Attribute-Based Access Control policy engine
│       │   │   ├── operations/         # Asynchronous Job Worker, DLQ & retry logic
│       │   │   ├── zk/                 # Zero-Knowledge range/predicate evaluator
│       │   │   ├── audit/              # SHA-256 hash-chained immutable audit ledger
│       │   │   └── security/           # Token signing, rate limiting & anti-tampering
│       │   ├── db/                     # Database Models & Session Management
│       │   │   ├── models.py           # SQLAlchemy entity definitions
│       │   │   └── session.py          # PostgreSQL / SQLite connection pool & migrations
│       │   ├── schemas/                # Pydantic v2 Request/Response contracts
│       │   ├── main.py                 # FastAPI Application Entrypoint & Middleware
│       │   └── worker_main.py          # Standalone background worker process
│       ├── tests/                      # Backend Unit & Integration Tests (Pytest)
│       ├── requirements.txt            # Python production dependencies
│       ├── pyproject.toml              # Build & Ruff linter configuration
│       └── Dockerfile
│
├── infrastructure/                     # Container & Local Orchestration
│   ├── docker-compose.yml              # Local multi-service composition (Web, API, Worker, DB, Redis)
│   └── postgres/init.sql               # Database initialization & initial schemas
│
├── tests/                              # Monorepo Automated Test Suites
│   ├── browser/                        # 14 Browser Acceptance Scenario Specifications (.md)
│   ├── run_all_tests.py                # 44-Suite Master Test Orchestrator
│   ├── test_phase01_foundation.py ... test_phase38_builder_brief.py
│   └── test_playwright_e2e.py          # Playwright test execution bridge
│
├── scripts/                            # Release & Verification Tooling
│   ├── hackathon_check.py              # Builder Brief 12-Check Automated Release Gate
│   ├── seed_demo_data.py               # Deterministic seed data populator
│   └── generate_test_tokens.py         # Test keypair & proof minting utility
│
├── docs/                               # Authoritative Documentation Suite
│   ├── architecture/                   # Engineering & System Specifications
│   │   ├── MASTER_ARCHITECTURE.md      # Platform Reference Architecture & Core Invariants
│   │   ├── REPOSITORY_STRUCTURE.md     # Directory & Subsystem Catalog (This Document)
│   │   ├── SYSTEM_FLOWCHARTS.md        # Comprehensive Mermaid Architecture & Sequence Diagrams
│   │   └── TEST_CASES_AND_VERIFICATION_MATRIX.md # Complete Monorepo Test Matrix
│   └── hackathon/                      # Hackathon Product & Evaluation Suite (26 Documents)
│       ├── README.md                   # Hackathon Master Index
│       ├── PROBLEM.md                  # Problem Statement & System Inefficiencies
│       ├── FLAGSHIP_JOURNEY.md         # 7-Screen Scholarship Application Journey
│       ├── VERIFICATION.md             # Cryptographic Verification & Negative Proofs
│       ├── PRIVACY.md                  # Zero Raw Document Transfer & Anti-Leakage
│       ├── ACCESSIBILITY.md            # UX4G 3.0, WCAG 2.2 AA & Data Saver Mode
│       ├── DEMO_SCRIPT.md              # 3-Minute Live Jury Walkthrough Script
│       ├── PHASE_39_BROWSER_DEMO_CERTIFICATION.md # Phase 39 Sign-Off
│       └── FINAL_RELEASE_VERIFICATION_REPORT.md   # Official Certification Report
│
├── render.yaml                         # Cloud 1-Click Deployment Blueprint (Render)
├── DEPLOYMENT.md                       # Production & Sandbox Deployment Guide
└── README.md                           # Main Project Readme & Quickstart
```

---

## 2. Core Subsystems Catalog

### A. Sovereign Citizen Gateway & Auth Subsystem
- **Path**: `services/api/app/api/v1/auth.py`, `apps/web/src/features/auth/`
- **Capabilities**:
  - 1-Click Demo Persona authentication (Rahul Sharma, Priya Verma, CBSE Authority, Delhi University, Admin).
  - Mobile OTP simulation (`123456`) with zero external telecom dependency.
  - JWT session issuance with role-based claim bounds and sovereign account IDs (`DIN-DEMO-001`).

### B. Cryptographic Trust & Verification Subsystem
- **Path**: `services/api/app/core/crypto/`, `services/api/app/api/v1/verification.py`
- **Capabilities**:
  - **Ed25519** asymmetric digital signatures for credential issuance and proof tokens.
  - **RFC 8785 (JCS)** JSON Canonicalization Scheme for deterministic claim digest generation.
  - **AES-256-GCM** envelope encryption for private payload transit.
  - **Zero-Knowledge Predicate Engine**: Evaluates range assertions (e.g. `income < 250000`, `age >= 18`) without revealing underlying numerical values.

### C. Flagship Public Service & Scholarship Subsystem
- **Path**: `services/api/app/api/v1/public_service.py`, `apps/web/src/features/scholarship/`
- **Capabilities**:
  - 7-Screen seamless scholarship application journey.
  - Automatic vault discovery of 4 required credentials (Identity, Domicile, Income, Academic).
  - Explicit Sharing Review screen separating shared predicates from withheld PII.
  - 0 raw document upload invariant (0 bytes transferred across the network).

### D. Negative Proof & Verification Laboratory
- **Path**: `services/api/app/api/v1/public_service.py`, `apps/web/src/features/demo-lab/`
- **Capabilities**:
  - Live interactive tamper demonstration: Modifying `income_eligible` immediately triggers `SIGNATURE INVALID ✕`.
  - Rejection verification for Expired Proofs ($TTL = 24\text{h}$), Revoked Certificates, and Wrong Audience presentation.
  - `⚡ 1-Click Sandbox Reset` endpoint restoring deterministic state in $< 50\text{ms}$.

### E. Asynchronous Document Processing Pipeline & Worker Engine
- **Path**: `services/api/app/core/operations/job_worker.py`, `services/api/app/worker_main.py`
- **Capabilities**:
  - 7-Stage pipeline: `MALWARE_SCAN` $\to$ `OCR` $\to$ `CLASSIFY` $\to$ `EXTRACT` $\to$ `DUPLICATE_CHECK` $\to$ `ISSUER_LOOKUP` $\to$ `VERIFICATION`.
  - Exponential backoff with jitter retry mechanism and Dead-Letter Queue (DLQ).
  - Standalone background worker process for decoupled operations.

### F. Immutable Hash-Chained Audit Ledger
- **Path**: `services/api/app/core/audit/`, `apps/web/src/components/consent/`
- **Capabilities**:
  - SHA-256 hash-linked audit blocks: $H(E_n \parallel H_{n-1})$.
  - Cryptographic tamper-evidence: modifying any historical event invalidates downstream hashes.
  - Real-time citizen consent audit trail and instantaneous revocation.
