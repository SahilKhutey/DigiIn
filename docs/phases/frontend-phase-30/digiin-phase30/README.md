# DigiIn — Phase 30: Long-Term Digital Trust Infrastructure

Canonical digital trust model, stable non-semantic DigiIn Account ID (`DGI-XXXXXXXXXXXX`), portable credential lifecycle with history-preserving supersession, universal domain-namespaced claim registry (`<domain>.<claim>`), national trust registry, advanced 4-tier proof engine (Type A to Type D), subject-controlled consent dashboard, platform governance committees, versioned platform contracts, DigiIn Platform SDK, and formal 9-layer reference architecture.

## Key Subsystems

1. **Canonical Trust Model & Account Layer (`DigiInAccount`, `PortableCredentialManager`)**:
   - Freezes permanent domain entity graph and enforces stable opaque account IDs (`DGI-XXXXXXXXXXXX`).
2. **Universal Claim Registry (`UniversalClaimRegistry`)**:
   - Enforces `<domain>.<claim>` namespace taxonomy and versioned field schema validation.
3. **National Trust Registry (`NationalTrustRegistry`)**:
   - Authoritative registry of trusted ecosystem participants, public keys, and accreditation levels.
4. **Advanced Proof Engine (`AdvancedProofEngine`)**:
   - 4-tier proof engine supporting Type A (Full), Type B (Predicate), Type C (Eligibility boolean), and Type D (Minimal Status).
5. **Subject-Controlled Trust & Consent (`SubjectControlledConsentManager`)**:
   - Citizen trust center managing active consents, expiration windows, and instant revocation.
6. **Platform Governance (`PlatformGovernanceEngine`)**:
   - Committee-governed versioned policy lifecycle (`Policy`, `Security`, `Privacy`, `Technical Standards`).
7. **Versioned Platform Contracts (`VersionedContractManager`)**:
   - Formal API/Event/Schema versioning (`ACTIVE`, `DEPRECATED`, `SUNSET`) and backward compatibility guarantees.
8. **DigiIn Platform SDK (`DigiInPlatformSDK`)**:
   - Standardized client SDK methods and universal error codes for institutional developers.
9. **9-Layer Formal Reference Architecture (`PlatformReferenceArchitecture`)**:
   - Encodes the 9 canonical platform layers and certifies v1 production readiness.

## Run with Docker

```bash
docker compose up -d
```
