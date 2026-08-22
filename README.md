# DigiIn

[![CI Pipeline](https://github.com/SahilKhutey/DigiIn/actions/workflows/ci.yml/badge.svg)](https://github.com/SahilKhutey/DigiIn/actions/workflows/ci.yml)
[![Security Audit](https://github.com/SahilKhutey/DigiIn/actions/workflows/security.yml/badge.svg)](https://github.com/SahilKhutey/DigiIn/actions/workflows/security.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

DigiIn is a citizen-side **document lifecycle and trust platform** for Indian public digital services. It helps a person receive, upload, verify, correct, recover and share trusted documents with clear provenance, consent and auditability.


## Status

This is a professional prototype foundation for Build What Moves India. It uses only fictional records and mock service states so the product flow can be designed, tested and improved safely before any authorised integration work.

## Product boundary

The first product slice is a **DigiLocker-style document recovery experience**:

1. A citizen selects a document and issuer.
2. DigiIn evaluates a diagnostic journey (identity, issuer lookup, document fetch, consent and destination callback).
3. The citizen receives a plain-language status, a responsible system layer and an appropriate recovery action.

This repository contains mock diagnostic data only. It must not collect Aadhaar numbers, OTPs, passwords, or government-account credentials.

The broader architecture treats recovery as one lifecycle path. Future authorised modules may support citizen uploads, government verification, legacy digitization, correction/version history and minimum-disclosure requester proofs.

## Workspace layout

| Path | Purpose |
| --- | --- |
| `apps/web` | Accessible React citizen interface |
| `services/api` | Modular FastAPI service for discovery, transactions, recovery, issuer health and consent previews |
| `packages/contracts` | Versioned cross-service JSON schemas |
| `packages/types` | Shared TypeScript contracts for web and future mobile clients |
| `data/examples` | Safe, fictional development fixtures |
| `docs` | Product, system, security and delivery decisions |

## Quick start

Copy `.env.example` to `.env`, then run the API and web app in separate terminals.

```powershell
cd services/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
uvicorn app.main:app --reload --port 8000
```

```powershell
cd apps/web
npm install
npm run dev
```

The API documentation is available at `http://localhost:8000/docs`; the web app runs at `http://localhost:5173`.

## Implemented API modules

| Area | Endpoint |
| --- | --- |
| Health | `GET /health` |
| Document discovery | `GET /api/v1/documents?q=` and `GET /api/v1/documents/{id}` |
| Scenarios | `GET /api/v1/scenarios` |
| Transaction diagnosis | `GET /api/v1/transactions/{id}/diagnosis` and `GET /api/v1/transactions/{id}/support-summary` |
| Recovery retry | `POST /api/v1/transactions/{id}/retry` |

| Trust context | `GET /api/v1/issuers/health` and `GET /api/v1/consents/preview` |
| Verification gateway | `POST /api/v1/verification/request`, `POST /api/v1/verification/request/{id}/authorize`, `GET /api/v1/verification/result/{id}` |
| Proof validation | `GET /api/v1/verification/token/{id}` and `POST /api/v1/verification/introspect` |
| Public JWKS discovery | `GET /.well-known/jwks.json` and `GET /api/v1/.well-known/jwks.json` |
| Platform foundation | `GET /api/v1/platform/snapshot` and `POST /api/v1/platform/demo/student` |

| Upload and review demo | `POST /api/v1/documents/upload`, `POST /api/v1/documents/{id}/classify`, `POST /api/v1/documents/{id}/verification-case`, `POST /api/v1/verification/cases/{id}/decision` |
| Correction & versioning | `POST /api/v1/documents/{id}/corrections`, `GET /api/v1/documents/{id}/versions`, `GET /api/v1/corrections`, `POST /api/v1/corrections/{id}/decision` |
| Citizen wallet & trust signals | `GET /api/v1/wallet/documents` |
| Document upload & OCR pipeline | `POST /api/v1/documents/upload-pipeline` |
| Government verifier console | `GET /api/v1/verifier/queues`, `GET /api/v1/verifier/cases`, `GET /api/v1/verifier/cases/{id}/comparison`, `POST /api/v1/verifier/cases/{id}/decision` |
| Aadhaar eKYC gateway | `POST /api/v1/ekyc/generate-otp`, `POST /api/v1/ekyc/verify-otp`, `POST /api/v1/ekyc/match-demographics` |
| Consent & token revocation | `GET /api/v1/consent`, `POST /api/v1/consent/{id}/revoke` |
| Sovereign audit trail | `GET /api/v1/audit/events` |

## Continuous Integration & Automated Testing

DigiIn includes a GitHub Actions CI pipeline running across matrix environments:

- **Backend Pytest Suite**: 18 unit & cryptographic validation tests (`pytest`).
  ```powershell
  cd services/api
  $env:PYTHONPATH="."; python -m pytest
  ```
- **Frontend Typecheck & Production Build**:
  ```powershell
  cd apps/web
  npm run build
  ```
- **Playwright End-to-End Browser Automation**: 11 full-journey user scenario specs.
  ```powershell
  cd apps/web
  npx playwright test
  ```

## Database & Storage


DigiIn includes a persistent relational database layer built with **SQLAlchemy 2.0**:
- **SQLite (Default)**: Out-of-the-box local storage file `./digiin_database.db` with automated table initialization and seed fixtures.
- **PostgreSQL**: Configure `DIGIIN_DATABASE_URL="postgresql://user:password@localhost:5432/digiin"` in your environment.

## Engineering guardrails


- Use anonymised/synthetic fixtures in development and test environments.
- Treat government integrations as explicit, consented adapters—not screen-scraping targets.
- Keep document, file, verification result and version history separate.
- Never present a citizen-uploaded file as government-issued or government-verified.
- Prefer purpose-bound proof tokens over raw document transfer.
- Build every feature through UI, API, domain logic, transaction, event/audit and validation.
- Build accessibility to WCAG 2.2 AA and use clear, multilingual-ready content.
- Keep diagnostic events auditable while minimising personal data.

## License

Released under the [MIT License](LICENSE).

Read the [documentation index](docs/README.md), [foundation architecture](docs/foundation-architecture.md), [principles](docs/principles.md), [security baseline](docs/security.md), and [product scope](docs/product-scope.md) before expanding the system.
