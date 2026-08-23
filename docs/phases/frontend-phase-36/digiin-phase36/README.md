# DigiIn — Phase 36: Verification Hardening, Negative Proof & Hackathon Readiness

Verification Lab (`/admin/verification-lab` / `/dev/verification`), deterministic negative proof demonstrations (Valid, Tampered, Untrusted, Revoked, Expired, Denied), minimal disclosure privacy auditing, pre-seeded dual-browser demo environment, and comprehensive hackathon documentation package.

## Key Subsystems

1. **Cryptographic Fixtures (`CryptographicFixtureRegistry`, `KeypairFixture`)**:
   - Pre-generated authentic Ed25519 keypairs, RFC 8785 canonical serialization, and SHA-256 digest assertions.
2. **Negative Proof Engine (`NegativeProofEngine`)**:
   - Mathematical validation proving that altered claims or corrupted digests deterministically fail verification (`INVALID`).
3. **Privacy Proof Validator (`PrivacyProofValidator`)**:
   - Validates selective & minimal disclosure: asserts zero unrequested claims, no raw file leakage, and clean masking.
4. **Verification Lab Test Harness (`VerificationLabService`)**:
   - Powers `/admin/verification-lab` for live jury walkthroughs across positive and negative test cases (`TC-01` through `TC-05`).
5. **Hackathon Demo Environment (`HackathonDemoEnvironment`)**:
   - Pre-seeded realistic demo state (Citizen Rahul Sharma `DGI-7K4M-X9P2-2026`, University of Delhi, National Scholarship Portal).

## Run with Docker

```bash
docker compose up -d
```
