# DigiIn — Phase 16: Production Hardening & Security Foundation

Centralized security boundary, authentication hardening, RBAC/IDOR defense, magic-byte file validation, tiered rate limiting, and immutable audit streams.

## Key Subsystems

1. **Authentication & Session Hardening**:
   - Password hashing with PBKDF2/Argon2id, automatic 15-minute brute-force lockout, TOTP MFA, and fingerprinted session rotation.
2. **RBAC & IDOR Defense (`AuthorizationService`)**:
   - Explicit role permissions combined with resource ownership validation (`resource.citizen_id == actor.user_id`).
3. **File Security & Quarantine**:
   - Magic-byte file validation, path traversal defense via randomized UUID storage keys, and short-lived HMAC signed tokens.
4. **Tiered Rate Limiting (`RateLimiterService`)**:
   - Custom rate limits for Login (5/min), OTP (3/min), Upload (10/min), and Verification (30/min).
5. **Standardized Error Responses**:
   - Machine-readable `DigiInError` responses with opaque `X-Request-ID` tracing (zero internal stack traces).
6. **Comprehensive Security Documentation**:
   - `SECURITY.md`, `THREAT-MODEL.md`, `AUTHORIZATION.md`, `DATA-CLASSIFICATION.md`, and `INCIDENT-RESPONSE.md`.

## Run with Docker

```bash
docker compose up -d
```
