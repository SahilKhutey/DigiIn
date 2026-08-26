# DigiLocker X (DigiIn) — Production & Sandbox Deployment Guide

## 1. Deployment Architecture

DigiLocker X (DigiIn) is packaged for 1-click cloud deployment on Render (or any standard Docker / Container / Kubernetes host) with deterministic sandbox mock providers:

```
                               PUBLIC INTERNET
                                      │
                                      ▼
                        https://<public-digiin-url>
                                      │
                                      ▼
                             ┌─────────────────┐
                             │   digiin-web    │ (Vite / React Static Site)
                             └────────┬────────┘
                                      │
                                      ▼
                             ┌─────────────────┐
                             │   digiin-api    │ (FastAPI / Python 3.12)
                             └────────┬────────┘
                                      │
                 ┌────────────────────┼────────────────────┐
                 ▼                    ▼                    ▼
          ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
          │  digiin-db   │     │digiin-worker │     │Demo Providers│
          │ (PostgreSQL) │     │  (Job Queue) │     │ (CBSE / KYC) │
          └──────────────┘     └──────────────┘     └──────────────┘
```

---

## 2. 1-Click Deployment via Render Blueprint

The repository contains a native [`render.yaml`](./render.yaml) blueprint configuring:
1. **`digiin-web`**: Static web application built from `apps/web/dist` with automatic API hostname discovery.
2. **`digiin-api`**: FastAPI REST API service with `/health` and `/ready` probes.
3. **`digiin-worker`**: Asynchronous background job worker for OCR, verification, and hash-chain audits.
4. **`digiin-db`**: PostgreSQL relational database.

### Quick Deployment Steps:
1. Connect your GitHub account to [Render Dashboard](https://dashboard.render.com/).
2. Select **Blueprints** $\to$ **New Blueprint Instance**.
3. Select repository **`SahilKhutey/DigiIn`** (Branch: `main`).
4. Render automatically parses `render.yaml` and provisions all 4 services.
5. Once deployed, Render generates a public HTTPS URL (e.g. `https://digiin-web.onrender.com`).

---

## 3. Environment Variables & Sandbox Configuration

| Variable | Target Service | Value | Purpose |
|---|---|---|---|
| `NODE_ENV` | `digiin-web` | `production` | Production frontend optimization |
| `DEMO_MODE` | All | `true` | Enables deterministic hackathon demo persona & reset |
| `MOCK_AUTH` | `digiin-api` | `true` | Bypasses external SMS OTPs; enables 1-click personas |
| `MOCK_KYC` | `digiin-api` | `true` | Simulated eKYC demographic matching (`KYC-DEMO-001`) |
| `MOCK_GOVERNMENT_APIS` | `digiin-api` | `true` | Local CBSE, Revenue, and Transport sandbox registries |
| `MOCK_NOTIFICATIONS` | `digiin-api` | `true` | In-app mock notification dispatcher |
| `DIGIIN_DATABASE_URL` | `digiin-api` | `fromDatabase: digiin-db` | Connection string to PostgreSQL / SQLite |

---

## 4. Free-Tier Cold Start & Pre-Demo Check

> [!NOTE]
> Free-tier Render web services spin down after 15 minutes of inactivity. The initial request wakes the instance within ~45-60 seconds.

### Pre-Judging Warm-Up:
1. Open `https://<public-digiin-url>` in browser.
2. Verify `/health` returns `{"status": "connected", "dialect": "..."}`.
3. Click `⚡ 1-Click Sandbox Reset` in the Demo Control Center (`/demo-lab`).
4. Begin live evaluation with immediate zero-latency responses.

---

## 5. Public Smoke Test Checklist

- [ ] **Home Page**: Renders branding, UX4G 3.0 banner, and CTA (*"Start Verification Journey"*).
- [ ] **Services Catalog**: Search, category filters, and *"Apply with DigiIn"* button active.
- [ ] **1-Click Authentication**: Instant persona sign-in as `Rahul Sharma (DIN-DEMO-001)`.
- [ ] **Flagship Scholarship Flow**: Discovers 4 verified credentials, reviews sharing, approves consent, and generates proof with **0 raw bytes uploaded**.
- [ ] **Cryptographic Verification**: Verifies valid proof $\to$ `VERIFIED`.
- [ ] **Tamper Defense**: Injects claim modification $\to$ `SIGNATURE INVALID ✕`.
- [ ] **1-Click Reset**: Resets state deterministically.
