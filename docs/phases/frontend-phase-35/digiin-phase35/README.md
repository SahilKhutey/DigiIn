# DigiIn — Phase 35: Web Pages + User Services Sites Interface + Working Implementation

Complete multi-tier connected web platform:
1. **Public Trust Website**: Hero landing, How DigiIn Works (`/how-it-works`), Public Services Directory (`/services`), Accredited Organizations Directory (`/organizations`), Security & Data Control (`/security`), and Help Center (`/help`).
2. **Authenticated Citizen Web App**: Action-oriented dashboard (`/dashboard`), Credentials wallet (`/credentials`), Request inbox tabs (`/requests`), Consent Center (`/consent`), Activity Timeline (`/activity`), and Security Settings.
3. **Service Partner Sites & Embeddable Verification Widget**: Embeddable widget (`<DigiInVerificationRequest />` / `"Continue with DigiIn"`) with secure authorization code exchange returning minimal verified claims.
4. **Institutional Operating Portal**: Department overview (`/institution`), 6-Step Stepper Wizard (`/institution/requests/new`), Review Queue (`/institution/review`), Team permissions (`/institution/team`), and Webhook integrations (`/institution/integrations`).

## Run with Docker

```bash
docker compose up -d
```
