# DigiIn — Phase 18: Cryptographic Proof & Verifiable Credentials

Multi-stage verifiable credentials, RFC 8785 JSON canonicalization, asymmetric Ed25519 digital signatures, key rotation with legacy proof support, trust registry, instant revocation, and privacy-preserving QR sharing.

## Key Subsystems

1. **Verified Claims & Data Minimization (`ClaimMinimizer`)**:
   - Typed assertions (`EDUCATION_VERIFIED`, `AGE_ELIGIBILITY = True`) disclosing only required facts without underlying PII.
2. **Canonicalization & Digest (`canonicalize_proof_payload`)**:
   - Deterministic RFC 8785 serialization ensuring byte stability across heterogenous platforms.
3. **Asymmetric Ed25519 Signing (`ProofSigningService`)**:
   - Canonical payload signing using Ed25519 private keys and SHA-256 binary digests.
4. **Multi-Stage Proof Verifier (`ProofVerifier`)**:
   - 6-stage sequence: Signature $\rightarrow$ Issuer Trust $\rightarrow$ Key Validity $\rightarrow$ Active Status $\rightarrow$ Expiration $\rightarrow$ Purpose Policy.
5. **Key Management & Rotation (`KeyManager`)**:
   - Active, rotating, retired, and revoked key states ensuring legacy proofs remain verifiable while compromised keys are immediately invalidated.
6. **Privacy-Preserving Proof Sharing & QR Resolver (`ProofShareService`)**:
   - Temporary share tokens and dynamic QR verification targets (`https://verify.digiin.in/share/:id`).

## Run with Docker

```bash
docker compose up -d
```
