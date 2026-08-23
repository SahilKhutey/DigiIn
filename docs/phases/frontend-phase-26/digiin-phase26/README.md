# DigiIn — Phase 26: DigiIn Trust Network & Interoperability

Authoritative issuer & verifier registries, scoped cross-organization trust relationships, immutable versioned claim schemas, verified claim lifecycles, audience-restricted presentation with anti-replay nonces, authoritative claim status registry, standardized trust protocol interoperability adapter, and anti-enumeration security.

## Key Subsystems

1. **Authoritative Issuer Registry (`IssuerRegistry`)**:
   - Manages accredited issuers across 5 trust levels (Level 0-4) and supported claim types.
2. **Authorized Verifier Registry (`VerifierRegistry`)**:
   - Governs verifier organizations, permissible operational purposes, and API scopes.
3. **Scoped Trust Relationships (`TrustRelationshipEngine`)**:
   - Manages explicit, scoped trust agreements between Issuers and Verifiers bounded by claim types, purposes, and validity windows.
4. **Immutable Claim Schema Registry (`ClaimSchemaRegistry`)**:
   - Validates claims against versioned schemas (`education.degree`, `identity.age_over_18`, `licence.driving`).
5. **Verified Claim Issuance Engine (`ClaimIssuanceEngine`)**:
   - Handles claim creation, assurance levels (`LOW` to `VERY_HIGH`), and status lifecycles (`ACTIVE`, `EXPIRED`, `REVOKED`).
6. **Audience-Restricted Claim Presentation (`ClaimPresentationEngine`)**:
   - Packages tamper-evident claim presentations bound to specific verifiers, purposes, and anti-replay nonces.
7. **Trust Protocol Interoperability Adapter (`TrustProtocolAdapter`)**:
   - Standardizes public trust operations (`issue_claim`, `present_claim`, `verify_claim`, `check_status`).
8. **Trust Security & Anti-Enumeration Guard (`AntiEnumerationGuard`, `TrustNetworkMonitor`)**:
   - Throttles blind citizen account probes and tracks trust network KPIs.

## Run with Docker

```bash
docker compose up -d
```
