# DigiIn — 5–7 Minute Live Demonstration Script

## 🎬 Dual-Browser Live Walkthrough

### Browser 1: Citizen (Rahul Sharma)
- URL: `http://localhost:5173/dashboard`
- Account ID: `DGI-7K4M-X9P2-2026`
- Pre-loaded: Bachelor of Technology in Computer Science (Degree Credential)

### Browser 2: Institutional Verifier (National Scholarship Portal)
- URL: `http://localhost:5173/services`

---

## ⏱️ Step-by-Step Flow

1. **0:00 — Problem Statement**: Explain how citizens must currently upload copies of marksheets and identity cards to dozens of different portals.
2. **1:00 — Service Requests Verification**: National Scholarship Portal creates a verification request for `DGI-7K4M-X9P2-2026` requesting `education.degree` and `education.graduationYear`.
3. **2:30 — Citizen Reviews & Consents**: Citizen receives in-app notification, reviews requested claims, and clicks `[Allow & Verify]`.
4. **3:30 — DigiIn Verifies Cryptographically**: DigiIn validates issuer Ed25519 signature and SHA-256 digest integrity against the Trust Registry.
5. **4:30 — Minimal Disclosure Delivery**: Scholarship Portal receives `{ "status": "VERIFIED", "claims": { "education.degree": "VERIFIED" } }` with zero unrequested PII or raw PDFs.
6. **5:30 — Institutional Decision**: Department reviewer reviews the result and marks the application `APPROVED`.
7. **6:30 — Negative Test**: Open `/admin/verification-lab`, run tampered credential test, and show `INVALID` result.
