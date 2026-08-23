# DigiIn STRIDE & DREAD Threat Model

## 1. System Assets & Threat Actors

### Primary Assets
- Citizen Personal Data & Verified Credentials
- Raw Uploaded Document Binaries (Class 10/12, Driving Licences)
- Cryptographic Proof Signing Keys (Ed25519)
- Active Session & Refresh Tokens
- Audit Event Stream
- Organisation API Keys & Webhook Secrets

### Threat Actors
- **Anonymous External Attacker**: Seeks public endpoint exploitation, credential brute-forcing, or denial of service.
- **Malicious Citizen**: Attempts privilege escalation, uploading malicious files, or IDOR access to another citizen's records.
- **Compromised Organisation Verifier**: Attempts to query documents outside granted consent scope or harvest citizen PII.
- **Malicious Provider / Man-in-the-Middle**: Attempts to inject forged verification payloads or replay webhook events.

---

## 2. STRIDE Threat Analysis & Mitigations

| Category | Threat Scenario | Impact | Applied DigiIn Mitigation |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Forged verification proof token presented to relying party | High | Cryptographic Ed25519 asymmetric signature with key registry validation. |
| **Tampering** | Modification of document payload in transit or at rest | High | SHA-256 binary checksum calculated on ingestion and validated against provenance. |
| **Repudiation** | Organisation denies requesting or inspecting citizen credentials | Medium | Append-only immutable audit trail recording actor ID, request ID, and timestamp. |
| **Information Disclosure** | IDOR access allowing Citizen A to view Citizen B's certificate | High | Strict resource ownership check enforcing `resource.citizen_id == actor.user_id`. |
| **Denial of Service** | Volumetric brute-force on login or verification endpoints | Medium | Tiered token bucket rate limiters and automatic 15-minute account lockout. |
| **Elevation of Privilege** | Verifier role attempting system administration or key rotation | Critical | Strict RBAC permission matrix verified at controller ingress. |

---

## 3. DREAD Risk Scoring

1. **Proof Forgery**: Damage=9, Reproducibility=1, Exploitability=2, AffectedUsers=9, Discoverability=2 $\rightarrow$ **Overall: Low Risk (Cryptographically Mitigated)**
2. **IDOR via Direct ID Query**: Damage=8, Reproducibility=8, Exploitability=6, AffectedUsers=5, Discoverability=5 $\rightarrow$ **Overall: Mitigated by Resource Access Guard**
3. **Malicious Executable Upload**: Damage=8, Reproducibility=7, Exploitability=5, AffectedUsers=4, Discoverability=6 $\rightarrow$ **Overall: Mitigated by Magic-Byte Validation**
