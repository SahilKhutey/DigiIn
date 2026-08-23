# DigiIn Frontend — Phase 2: Design System & Modular Architecture

Phase 2 converts the monolithic prototype into a **modular, reusable UX4G 3.0 component architecture** while preserving the zero-dependency, instant-run capability.

## Run

```bash
# From Frontend Phase 2 directory
npm run dev
# or: python -m http.server 4174
```

Then open `http://localhost:4174`.

## What Was Added in Phase 2

1. **Modular JS Components (`src/components/`)**:
   - `Button.js` (variants: primary, secondary, outline, danger, ghost, loading)
   - `Card.js` (variants: default, elevated, bordered, highlight)
   - `Badge.js` (multi-modal status: `✓ Verified`, `◷ Pending`, `✕ Mismatch`, `ℹ Info`)
   - `Alert.js` (accessible alert banners with recovery actions)
   - `DocumentCard.js` (document metadata, issuer, and Level 0-4 trust tier)
   - `ConsentCard.js` (granular purpose-bound consent with Zero-Knowledge toggle)
   - `DigiInIDCard.js` (sovereign DIN identifier presentation with QR code placeholder)
   - `VerificationTimeline.js` (asynchronous multi-stage progress pipeline)
   - `ShareVerificationCard.js` (verifiable proof reference receipt `DLV-XXXX-XXXX`)

2. **Component-Specific Styles (`src/styles/components.css`)**:
   - Dedicated styling for each component adhering to the 4px grid and WCAG 2.1 AA contrast ($\ge 4.5:1$).

3. **Complete Citizen Journey & Views**:
   - `#/` (Landing)
   - `#/sign-in` (Passwordless Mobile OTP Login)
   - `#/dashboard` (Citizen Vault & DigiIn ID)
   - `#/verify` (Verification Request & Scope)
   - `#/consent` (Granular Consent Configuration)
   - `#/progress` (Multi-stage Async Pipeline)
   - `#/result` (3-Second Result Hero & Receipt)
   - `#/how`, `#/security`, `#/accessibility`, `#/privacy`, `#/terms`, `#/help`
