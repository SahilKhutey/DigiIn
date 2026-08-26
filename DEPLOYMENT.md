# DigiIn (DigiLocker X) — Production & Sandbox Deployment Guide

> **Official Builder Brief Target**: Zero-access-request public URL on Vercel, 1-click reviewer authentication, zero raw document transfers, and 100% verified canonical citizen journey.

---

## 1. Canonical Hackathon Architecture

```
                       PUBLIC INTERNET (Judges & Reviewers)
                                        │
                                        ▼
                            https://digiin.vercel.app
                                        │
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │                  VERCEL                   │
                  │         DigiIn Web Application            │
                  │          (React 19 / Vite SPA)            │
                  └─────────────────────┬─────────────────────┘
                                        │
                                 HTTPS (API Calls)
                                        │
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │                  RENDER                   │
                  │         DigiIn REST API Service           │
                  │         (FastAPI / Python 3.12)           │
                  └─────────────────────┬─────────────────────┘
                                        │
                               DIGIIN_DATABASE_URL
                                        │
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │                 SUPABASE                  │
                  │           PostgreSQL Database             │
                  │   (Accounts, Credentials, Consents, Proofs)│
                  └───────────────────────────────────────────┘
```

---

## 2. Infrastructure Responsibilities

| Tier | Provider | Directory | Deployment Role |
|---|---|---|---|
| **Presentation** | **Vercel** | `apps/web` | Public Citizen UI, 1-click login, service discovery, scholarship flow |
| **Logic & Verification** | **Render** | `services/api` | REST API, Ed25519 cryptography, verification engine, /health check |
| **Persistence** | **Supabase** | `supabase/` | PostgreSQL relational storage, migrations, and synthetic seed fixtures |

---

## 3. Step-by-Step Deployment Sequence

### Step 1: Configure Supabase (PostgreSQL Persistence)
1. Open [Supabase Dashboard](https://supabase.com/dashboard) $\to$ **New Project** (`DigiIn`).
2. Go to **Project Settings** $\to$ **Database** $\to$ **Connection String** (URI mode / Transaction Pooler).
3. Copy your PostgreSQL URI: `postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`.
4. Run migrations via GitHub Integration (`supabase/migrations/`) or Supabase SQL Editor (`supabase/seed.sql`).

### Step 2: Deploy Backend on Render (FastAPI Web Service)
1. Open [Render Dashboard](https://dashboard.render.com/) $\to$ **New Web Service**.
2. Connect repository **`SahilKhutey/DigiIn`** (Branch: `main`).
3. Set configuration:
   - **Name**: `digiin-api`
   - **Root Directory**: `services/api`
   - **Runtime**: `Python` (or `Docker` using `services/api/Dockerfile`)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
4. Set Environment Variables:
   - `ENVIRONMENT`: `production`
   - `DEMO_MODE`: `true`
   - `MOCK_AUTH`: `true`
   - `MOCK_KYC`: `true`
   - `MOCK_GOVERNMENT_APIS`: `true`
   - `MOCK_NOTIFICATIONS`: `true`
   - `DIGIIN_DATABASE_URL`: *Your Supabase PostgreSQL Connection String*
   - `ALLOWED_ORIGINS`: `https://digiin.vercel.app,https://*.vercel.app`
5. Note your Render URL (e.g. `https://digiin-api.onrender.com`).

### Step 3: Deploy Frontend on Vercel (Citizen Web Application)
1. Open [Vercel Dashboard](https://vercel.com/new) $\to$ Import **`SahilKhutey/DigiIn`**.
2. Configure settings:
   - **Project Name**: `digiin`
   - **Framework Preset**: `Vite`
   - **Root Directory**: `apps/web`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Add Environment Variable:
   - `VITE_API_BASE_URL`: `https://digiin-api.onrender.com` *(your Render API URL)*
4. Click **Deploy**. Vercel will output your public URL (`https://digiin.vercel.app`).

---

## 4. Reviewer & Judge Access Credentials

Reviewers can access all features immediately with 1-click persona buttons:

| Role | Persona Name | DigiIn ID | Mobile | OTP | Primary Evaluation Scenario |
|---|---|---|---|---|---|
| **Default Citizen** | Rahul Sharma | `DIN-DEMO-001` | `9876543210` | `123456` | Delhi University Scholarship application with 0 raw bytes transferred |
| **Subsidies Citizen** | Priya Verma | `DIN-DEMO-002` | `9876500000` | `123456` | PM-Kisan & Domicile income verification |
| **Institutional Verifier** | Delhi University | `ORG-DEMO-001` | `9876511111` | `123456` | Verifier console & proof token introspection |
| **Authoritative Issuer** | CBSE Authority | `ISS-DEMO-CBSE` | `9876522222` | `123456` | Official Class XII credential issuance |
| **Platform Operator** | Root Administrator | `ADMIN-DEMO-01` | `9876599999` | `123456` | Health checks, cryptographic registry & audit logs |

---

## 5. End-to-End Black-Box Verification Checklist

Execute this verification on a clean browser in private/incognito mode before final submission:

- [ ] **1. Public URL Access**: `https://digiin.vercel.app` opens instantly without access requests or VPN.
- [ ] **2. Safety Disclosure**: Top banner clearly indicates synthetic prototype mode.
- [ ] **3. 1-Click Login**: Click *"Rahul Sharma"* on the Sign In page $\to$ instant dashboard redirect.
- [ ] **4. Document Discovery**: View 4 pre-issued verified documents in Citizen Wallet.
- [ ] **5. Service Discovery**: Go to Services Catalog $\to$ Select *"National Merit Scholarship"*.
- [ ] **6. Purpose-Bound Consent**: Review exact predicate claims being verified (Income < 8 LPA, Class XII Passed).
- [ ] **7. Cryptographic Verification**: Authorize $\to$ Ed25519 proof generated with **0 raw bytes transferred**.
- [ ] **8. Verifier Introspection**: Verify proof status shows `TRUSTED_PROOF_VERIFIED`.
- [ ] **9. Negative Proof Lab**: Go to Demo Lab $\to$ Test tampered signature $\to$ confirmed rejected.
- [ ] **10. 1-Click Reset**: Click `⚡ Reset Sandbox` $\to$ clean initial state restored.
