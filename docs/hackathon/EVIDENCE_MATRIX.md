# DigiLocker X (DigiIn) — Authoritative Evidence Matrix

## 1. The 5-Level Evidence Hierarchy

DigiLocker X distinguishes between superficial claims and mathematically verifiable proof through a strict 5-tier evidence hierarchy:

```
                            LEVEL 5: CRYPTOGRAPHIC EVIDENCE
                        Ed25519 Signatures │ RFC 8785 Digests │ SHA-256 Chain
                                           ▲
                                           │
                            LEVEL 4: LIVE DEMONSTRATION
                        Citizen Wallet │ Institution Verifier │ Negative Proof Lab
                                           ▲
                                           │
                            LEVEL 3: AUTOMATED PROOF
                        41-Suite Test Matrix │ Pytest │ Threat-Model Tests
                                           ▲
                                           │
                            LEVEL 2: IMPLEMENTATION
                        FastAPI Services │ TypeScript UI │ SQLite/Postgres Models
                                           ▲
                                           │
                            LEVEL 1: DOCUMENTATION
                        7 Master Specs │ Threat Model │ Phase Catalog
```

---

## 2. Comprehensive Evidence Mapping

| Platform Capability | Level 1: Documentation | Level 2: Implementation | Level 3: Automated Test Proof | Level 4: Demonstration Surface | Level 5: Cryptographic Guarantee |
|---|---|---|---|---|---|
| **Data Sovereignty & Encryption** | `docs/CoreFoundation.md`, `docs/DATA-CLASSIFICATION.md` | `app/core/security/encryption.py`, `app/core/operations/object_storage.py` | `tests/test_phase8_security_hardening.py`, `tests/test_phase9_operations_observability.py` | Citizen Vault & Document Upload | AES-256-GCM Envelope Encryption, per-document dynamic DEK under KEK |
| **Purpose-Bound Citizen Consent** | `docs/Workflow.md`, `docs/Principles.md` | `app/core/security/policy.py`, `app/services/trust.py` | `tests/test_phase17_production_workflow.py`, `tests/test_phase8_acceptance_scenario.py` | Citizen Request Inbox (`apps/web`) | Attribute-level scope constraints, 15m validity TTL |
| **Minimal Selective Disclosure** | `docs/Principles.md`, `docs/Workflow.md` | `app/core/security/privacy.py`, `app/core/proofs/claim_minimizer.py` | `tests/test_phase36_verification_hardening.py`, `tests/test_phase37_release_readiness.py` | Verifier Result View (`apps/verifier-console`) | Boolean predicate evaluation (`income_eligible: true`), Zero raw PII/PDF transfers |
| **Verifiable Proof Generation** | `docs/Proof-Contract.md`, `docs/Services.md` | `app/crypto/proofs.py`, `app/core/proofs/proof_signer.py` | `tests/test_phase18_cryptographic_proofs.py`, `tests/test_phase36_verification_hardening.py` | Verifier Claim Inspection | Ed25519 Digital Signatures, RFC 8785 Canonical JSON Serialization |
| **Negative Proof & Tamper Defense** | `docs/THREAT-MODEL.md`, `docs/security.md` | `app/core/verification_hardening/negative_proof_engine.py` | `tests/test_phase36_verification_hardening.py`, `tests/test_phase37_release_readiness.py` | Verification Lab Console | Mathematical digest mismatch, single-use anti-replay nonce tracking |
| **Government Issuer Integration** | `docs/Services.md`, `docs/Workflow.md` | `app/integrations/mock_providers.py`, `app/integrations/gateway.py` | `tests/test_external_integration_e2e.py`, `tests/test_phase19_real_provider_integration.py` | Issuer Console (`apps/issuer-console`) | Isolated adapter contracts, HMAC-SHA256 authenticated webhooks |
| **Production Scale & Observability** | `docs/CoreFoundation.md`, `docs/Services.md` | `app/core/operations/job_worker.py`, `app/core/operations/observability.py` | `tests/test_phase9_operations_observability.py`, `tests/test_phase9_acceptance_scenario.py` | Operations Dashboard (`/api/v1/ops/dashboard`) | Sliding-window token buckets, DLQ quarantine, RPO $\le 15$m, RTO $\le 60$m |
| **Tamper-Evident Audit Chain** | `docs/Database.md`, `docs/Services.md` | `app/core/security/audit_chain.py` | `tests/test_phase8_security_hardening.py`, `tests/test_phase37_release_readiness.py` | Admin Sovereign Audit Stream (`apps/admin`) | $H(\text{event}_n \parallel \text{hash}_{n-1})$ SHA-256 Hash Linked Chain |

---

## 3. Cryptographic Verification Command Line Reference

Third parties and judges can verify proof tokens completely offline:

```powershell
# Run standalone mathematical proof verification demo
python tests/cli_proof_verifier.py --demo

# Inspect public cryptographic trust anchors
python tests/cli_proof_verifier.py --jwks
```
