# DigiIn Frontend — Phase 4: Citizen Authentication & Session Foundation

UX4G 3.0 citizen authentication, 6-digit OTP verification, 30s countdown timer, first-time onboarding, and authenticated session management.

## Phase 4 Features

- Multi-step mobile authentication flow:
  1. 10-digit mobile number entry with `+91` prefix and format validation.
  2. 6-digit OTP verification screen with auto-focus and 30s countdown timer.
  3. Error recovery handling (invalid code alerts, remaining attempts, resend).
  4. First-time citizen profile onboarding (Aadhaar demographic eKYC simulation).
  5. Sovereign DigiIn ID assignment (`DIN-84K2-19Q7`).
  6. Authenticated citizen dashboard with trust posture metrics and document vault.
  7. Sign-out and session revocation.

## Run

```bash
cd "Frontend Phase 4/digiin-frontend"
python -m http.server 4176
```

Then open `http://localhost:4176`.
