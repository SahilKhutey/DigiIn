# DigiIn Frontend — Phase 5

UX4G-aligned frontend foundation for DigiIn's citizen document-verification experience.

## Phase 5

Implements the working **Verification Request → Review → DigiLocker connection → Consent → Document Retrieval → Documents Ready** journey.

### Included

- Organisation identity and verification request context
- Requested-document list with purpose and issuer
- Review-before-connection experience
- DigiLocker mock adapter/service boundary
- Connection and authentication handoff states
- Explicit consent and consent validity
- Consent decline-safe UX pattern
- Retrieval progress and accessible live status
- Documents-ready screen
- Responsive/mobile layouts
- Keyboard/focus/accessibility foundation

### Demo behavior

No real DigiLocker credentials or documents are processed. The service adapter simulates connection, authentication, consent retrieval, and document retrieval.

## Run

```bash
npm run dev
```

Open `http://localhost:4173`.
