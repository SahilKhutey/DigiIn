# DigiLocker X — Full Development Foundation

A runnable, modular foundation for a citizen-first digital credential,
document verification, consent, proof and government review platform.

## Included

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL-ready configuration
- SQLite development fallback
- JWT access + rotating refresh sessions
- RBAC
- Documents and document versions
- Credentials
- Verification requests
- Consent
- Mock government issuer
- Issuer adapter registry
- Government review queue
- Signed verification proofs
- Audit events
- Correction cases
- Notifications
- Health/readiness endpoints
- Background worker scaffold
- API versioning

### Web
- Next.js
- Citizen dashboard
- Documents
- Verification
- Consent
- Activity
- Correction
- Government review
- Requester verification
- Shared API client

### Mobile
- React Native / Expo starter
- Shared API configuration
- Citizen navigation foundation

### Infrastructure
- Docker Compose
- PostgreSQL
- Redis
- API
- Worker
- Web

## Run with Docker

```bash
docker compose up --build
```

Then:

- Web: http://localhost:3000
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Local backend

```bash
cd services/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Local web

```bash
cd apps/web
npm install
npm run dev
```

## API demo sequence

1. Register a citizen.
2. Login.
3. Create a demo credential.
4. Create a verification request.
5. Grant consent.
6. Run issuer verification.
7. Retrieve the proof.
8. Validate the proof.
9. Create a correction case if required.

## Production boundary

This is an engineering foundation, not a production DigiLocker replacement.
Government integrations, approved identity systems, cryptographic key management,
data retention policies, legal policies, accessibility audits, penetration testing,
and infrastructure controls must be completed before production use.
