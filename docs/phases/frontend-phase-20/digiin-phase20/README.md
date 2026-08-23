# DigiIn — Phase 20: Developer & API Platform

External developer and API platform exposing DigiIn's verification capabilities to external services, government departments, universities, enterprises, and approved third-party applications.

## Key Subsystems

1. **Developer Organizations & Applications (`DeveloperOrganization`, `DeveloperApplication`)**:
   - Manages organizational accounts, application registration, client IDs (`dgi_client_...`), and client secret hashing.
2. **OAuth 2.0 Authorization Server (`OAuthAuthorizationServer`)**:
   - Client credentials authentication issuing short-lived JWT access tokens with granular scopes (`verification:create`, `verification:education`, `proof:verify`, `proof:read`, `subject:resolve`).
3. **DigiIn Account ID Resolver (`AccountIdResolver`)**:
   - Non-sequential, non-guessable identity resolution (`DGI-7F8K-99MX`, `DGI-SBX-001`) with anti-enumeration defense and throttling.
4. **Verification & Consent Delegation Gateway (`DeveloperGateway`)**:
   - Manages verification lifecycle (`POST /v1/verifications`), citizen consent delegation, provider evidence retrieval, and proof minting.
5. **Webhook Notification Dispatcher (`WebhookDispatcher`)**:
   - Asynchronous webhook deliveries signed with HMAC-SHA256 headers (`X-DigiIn-Signature`, `X-DigiIn-Event-ID`, `X-DigiIn-Timestamp`).
6. **Multi-Tenant Isolation Guard (`MultiTenantGuard`)**:
   - Enforces strict resource ownership preventing cross-organization data leakage.
7. **Usage Metering & Rate Limiting (`UsageMeterService`)**:
   - Sliding window rate limiting and latency metrics.

## Run with Docker

```bash
docker compose up -d
```
