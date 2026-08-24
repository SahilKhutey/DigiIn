# DigiIn — Authoritative Submission Evidence & Judge Verification

## 1. The 5-Level Evidence Hierarchy

DigiIn backs all product claims with verifiable evidence across five rigorous tiers:

```
                            LEVEL 5: CRYPTOGRAPHIC PROOF
                        Ed25519 Signatures │ RFC 8785 Digests │ SHA-256 Chain
                                           ▲
                                           │
                            LEVEL 4: LIVE DEMONSTRATION
                        Citizen Wallet │ Institution Verifier │ Negative Proof Lab
                                           ▲
                                           │
                            LEVEL 3: AUTOMATED PROOF
                        43-Suite Test Matrix │ Pytest │ Threat-Model Tests
                                           ▲
                                           │
                            LEVEL 2: IMPLEMENTATION
                        FastAPI Services │ TypeScript UI │ SQLite/Postgres Models
                                           ▲
                                           │
                            LEVEL 1: DOCUMENTATION
                        12 Hackathon Specs │ 7 Master Specs │ Phase Catalog
```

---

## 2. Cryptographic Proof & Negative Evidence Lab

| Test Scenario | Action Tested | Mathematical Defense | Result |
|---|---|---|:---:|
| **Authentic Credential** | Baseline verified proof (`PRF-DEMO-1042`) | Ed25519 signature + RFC 8785 canonical digest valid | **`VERIFIED ✓`** |
| **Claim Tampering** | Modified `income_eligible` from `true` to `false` | Bit-level digest mismatch triggers signature failure | **`INVALID ✗`** |
| **Rogue / Untrusted Issuer** | Created credential with unregistered issuer DID | Trust Registry rejection | **`UNTRUSTED ✗`** |
| **Revoked Credential** | Presenting revoked domicile certificate | Real-time CRL status check | **`REVOKED ✗`** |
| **Expired Proof** | Presenting proof past its 24h validity window | Timestamp TTL expiration evaluation | **`EXPIRED ✗`** |
| **Privacy Leakage** | Payload attempting to disclose raw PDF or Aadhaar | Policy engine rejects forbidden claim disclosure | **`REJECTED ✗`** |

---

## 3. How to Reproduce All Evidence (1-Click Commands)

```powershell
# 1. Run Complete 43-Suite Monorepo Test Matrix
python tests/run_all_tests.py

# 2. Run Automated Builder Brief Verification Gate
python scripts/hackathon_check.py

# 3. Run Live Interactive Terminal Showcase
python scripts/hackathon_showcase.py

# 4. Verify Cryptographic Proofs Offline
python tests/cli_proof_verifier.py --demo
```
