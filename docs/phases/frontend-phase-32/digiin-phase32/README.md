# DigiIn — Phase 32: Product Verification System

Generic DigiIn product artifacts (credentials, certificates, badges, claims, records), opaque high-entropy identifiers (`DGP-XXXX-XXXX-XXXX`), Ed25519 cryptographic signatures with canonical digest hashing, modular 7-point verification checks (Existence, Issuer Trust, Signature, Integrity, Expiry, Revocation, Policy), product lifecycle management, QR reference resolution (`digiin://verify/DGP-...`), and public verification sanitization with anti-enumeration protection.

## Key Subsystems

1. **Generic DigiIn Product Model (`DigiInProduct`, `ProductType`)**:
   - Generic product artifacts with opaque non-sequential IDs (`DGP-XXXX-XXXX-XXXX`).
2. **Cryptographic Signing & Integrity (`ProductCryptoEngine`, `ProductSignature`)**:
   - RFC 8785 JSON canonicalization, SHA-256 digest computation, and Ed25519 asymmetric signatures.
3. **Product Lifecycle Manager (`ProductLifecycleManager`)**:
   - Manages product states (`ACTIVE`, `SUSPENDED`, `REVOKED`, `EXPIRED`, `SUPERSEDED`) with historical audit trails.
4. **Multi-Point Verification Check Matrix (`VerificationCheckUnits`)**:
   - Modular verification units: `ProductExists`, `IssuerTrust`, `Signature`, `Integrity`, `Expiration`, `Revocation`, `Policy`.
5. **Product Verification Engine (`ProductVerificationEngine`)**:
   - Orchestrates multi-check verification pipelines and returns `ProductVerificationResponse` with assurance levels.
6. **QR References & Public Data Sanitization (`QRVerifierHelper`, `PublicResponseSanitizer`)**:
   - Handles `digiin://verify/DGP-...` QR payloads and shields sensitive internal structures from public scraping.

## Run with Docker

```bash
docker compose up -d
```
