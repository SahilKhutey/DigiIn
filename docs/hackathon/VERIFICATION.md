# DigiIn — Verification & Negative Proof Evidence

DigiIn enforces deterministic cryptographic verification across 7 independent properties.

## 🔬 Deterministic Verification Matrix

| Scenario | Check Performed | Expected Outcome | Hackathon Lab Status |
| :--- | :--- | :--- | :--- |
| **Valid Credential** | Ed25519 Signature + SHA-256 Digest Match | `VERIFIED` | ✅ Passed (`TC-01`) |
| **Tampered Credential** | Claim modified after issuance | `INVALID` | ❌ Detected (`TC-02`) |
| **Untrusted Issuer** | Issuer ID not in National Trust Registry | `UNTRUSTED` | ❌ Rejected (`TC-03`) |
| **Revoked Credential** | Authoritative revocation record | `REVOKED` | ❌ Blocked (`TC-04`) |
| **Expired Credential** | Validity duration timestamp check | `EXPIRED` | ❌ Expired (`TC-05`) |
| **Consent Denied** | Citizen clicks `[Deny]` | `DENIED` | ❌ Zero Disclosure |

## 🧪 Verification Lab Route (`/admin/verification-lab`)

Judges and evaluators can run live interactive verification tests in the Verification Lab to prove that altered bytes or corrupted digests deterministically fail verification.
