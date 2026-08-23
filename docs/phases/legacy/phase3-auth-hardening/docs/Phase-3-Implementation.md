# DigiIn Phase 3 — Identity & Authentication Hardening

## Goal
Separate account authentication from verified identity, make sessions persistent, and remove implicit demo identity behavior from the domain.

## Components

### DigiInAccount
Opaque public account identifier plus internal database identity.

### AuthChallenge
Short-lived authentication challenge with:
- challenge ID
- account reference
- channel
- challenge hash
- expiry
- attempts
- consumed timestamp

### Session
Persistent session with:
- account reference
- refresh-token family
- hashed refresh token
- creation/expiry
- last use
- revocation

### IdentityClaim
A claim is not automatically authoritative. It has a verification level and source.

### SecurityEvent
Every authentication security transition is auditable.

## Rules
1. Never store raw OTP values.
2. Never store raw refresh tokens.
3. Never use a phone number or government identifier as the DigiIn Account ID.
4. Authentication does not equal government identity verification.
5. Demo authentication must be explicitly environment-gated.
6. Production requires an externally supplied signing/authentication secret or key provider.
7. Refresh token rotation must invalidate the previous token.
8. Reuse of a rotated refresh token revokes its token family.

## API target

POST /api/v1/auth/challenge
POST /api/v1/auth/verify
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/session

## Exit criteria

A test can create an account, authenticate through a challenge, access a protected route, rotate a refresh token, revoke a session, and prove that the old credentials no longer work.
