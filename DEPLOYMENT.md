# DigiLocker X (DigiIn) — Production & Sandbox Deployment Guide

> **Official Builder Brief Target**: Zero-access-request public URL, 1-click reviewer authentication, zero raw document leaks, and 100% working canonical citizen journey.

---

## 1. Hosting Options & Architecture

```
                                    PUBLIC INTERNET
                                           │
                                           ▼
                   ┌───────────────────────────────────────────────┐
                   │    Frontend: Vercel / Render Static Site      │
                   │        (https://<public-digiin-domain>)       │
                   └───────────────────────┬───────────────────────┘
                                           │
                                           ▼ HTTPS
                   ┌───────────────────────────────────────────────┐
                   │     Backend API: FastAPI / Python 3.12        │
                   │        (https://<public-api-domain>)          │
                   └───────────────────────┬───────────────────────┘
                                           │
                      ┌────────────────────┼────────────────────┐
                      ▼                    ▼                    ▼
               ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
               │  digiin-db   │     │digiin-worker │     │Demo Providers│
               │ (PostgreSQL) │     │ (Async Jobs) │     │ (CBSE / KYC) │
               └──────────────┘     └──────────────┘     └──────────────┘
```

---

## 2. Option A (Recommended): Dual Hosting (Vercel Frontend + Render API)

This configuration ensures **instant global CDN delivery with zero UI cold starts** on judges' browsers while delegating cryptographic and database workloads to Render.

### Step 1: Deploy Backend & Database on Render
1. Open [Render Dashboard](https://dashboard.render.com/) $\to$ **New Blueprint Instance**.
2. Connect repository **`SahilKhutey/DigiIn`** (Branch: `main`).
3. Render automatically provisions:
   - `digiin-api` (FastAPI Web Service)
   - `digiin-worker` (Background Job Worker)
   - `digiin-db` (PostgreSQL Database)
4. Note your API URL (e.g. `https://digiin-api.onrender.com`).

### Step 2: Deploy Frontend on Vercel
1. Open [Vercel Dashboard](https://vercel.com/new) $\to$ **Import Git Repository** (`SahilKhutey/DigiIn`).
2. Configure project settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `apps/web`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Add Environment Variable:
   - `VITE_API_BASE_URL` = `https://digiin-api.onrender.com` (your Render API URL)
4. Click **Deploy**. Vercel will output your instant public URL (e.g. `https://digiin.vercel.app`).

---

## 3. Option B: 1-Click Unified Render Blueprint

Deploy the entire monorepo (Static Frontend, REST API, Worker, PostgreSQL) via [`render.yaml`](./render.yaml):

1. Go to [Render Blueprints](https://dashboard.render.com/blueprints).
2. Select **`SahilKhutey/DigiIn`** $\to$ Click **Apply**.
3. Render automatically provisions all 4 services and links them together.
4. Access the web app at `https://digiin-web.onrender.com`.

---

## 4. Environment Variables Matrix

| Variable | Target Service | Value | Purpose |
|---|---|---|---|
| `NODE_ENV` | Frontend | `production` | Production asset optimization |
| `VITE_API_BASE_URL` | Frontend | `https://digiin-api.onrender.com` | Live backend API route target |
| `ENVIRONMENT` | API | `production` | Production API mode |
| `ALLOWED_ORIGINS` | API | `https://digiin.vercel.app,https://digiin-web.onrender.com` | Allowed CORS origins |
| `DEMO_MODE` | All | `true` | Enables deterministic hackathon fixtures & reset |
| `MOCK_AUTH` | API | `true` | Enables 1-click reviewer sign-in & OTP `123456` |
| `MOCK_KYC` | API | `true` | Simulated eKYC demographic matching |
| `MOCK_GOVERNMENT_APIS` | API | `true` | Local CBSE, Revenue, and Transport sandbox registries |
| `MOCK_NOTIFICATIONS` | API | `true` | In-app mock notification dispatcher |
| `DIGIIN_DATABASE_URL` | API | `fromDatabase: digiin-db` | Connection string to PostgreSQL / SQLite |

---

## 5. Reviewer & Judge Access Credentials

The submission uses pre-configured 1-click personas. Reviewers do not need to register, verify phone numbers, or upload documents:

| Role | Persona Name | DigiIn ID | Mobile | OTP | Scenario Focus |
|---|---|---|---|---|---|
| **Default Citizen** | Rahul Sharma | `DIN-DEMO-001` | `9876543210` | `123456` | Flagship Scholarship application & zero-knowledge proofs |
| **Subsidies Citizen** | Priya Verma | `DIN-DEMO-002` | `9876500000` | `123456` | PM-Kisan & Domicile income verification |
| **Institutional Verifier** | Delhi University Admissions | `ORG-DEMO-001` | `9876511111` | `123456` | Verifier console & proof introspection |
| **Authoritative Issuer** | CBSE Demo Authority | `ISS-DEMO-CBSE` | `9876522222` | `123456` | Academic credential issuance |
| **Platform Operator** | Root Administrator | `ADMIN-DEMO-01` | `9876599999` | `123456` | Health probes & immutable audit trail |

---

## 6. End-to-End Black-Box Verification Checklist

Execute this smoke test on a clean browser in incognito mode before final submission:

- [ ] **1. Public URL Access**: Opens immediately without access requests or VPN.
- [ ] **2. Safety Disclosure**: Top banner clearly indicates synthetic prototype mode.
- [ ] **3. 1-Click Login**: Click *"Rahul Sharma"* on the Sign In page $\to$ instant dashboard redirect.
- [ ] **4. Document Discovery**: View 4 pre-issued verified documents in Citizen Wallet.
- [ ] **5. Service Discovery**: Go to Services Catalog $\to$ Select *"National Merit Scholarship"*.
- [ ] **6. Purpose-Bound Consent**: Review exact predicate claims being verified (Income < 8 LPA, Class XII Passed).
- [ ] **7. Cryptographic Verification**: Authorize $\to$ Ed25519 proof generated with **0 raw bytes transferred**.
- [ ] **8. Verifier Introspection**: Verify proof status shows `TRUSTED_PROOF_VERIFIED`.
- [ ] **9. Negative Proof Lab**: Go to Demo Lab $\to$ Test tampered signature $\to$ confirmed rejected.
- [ ] **10. 1-Click Reset**: Click `⚡ Reset Sandbox` $\to$ clean initial state restored.
