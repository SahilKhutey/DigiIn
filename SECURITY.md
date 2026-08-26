# DigiIn (DigiLocker X) — Production Security Policy & Threat Model

## 🛡️ Executive Security Overview

DigiIn (DigiLocker X) is engineered around a **Zero-Trust, Zero-File-Transfer, and Minimal-Disclosure** architecture. The platform guarantees that citizens can authoritatively prove eligibility (e.g. academic qualifications, income thresholds, majority age) to verifier institutions **without transferring raw identity documents or leaking sensitive PII**.

---

## 🔐 Core Cryptographic & Security Invariants

The DigiIn repository enforces 8 automated security gates in CI/CD ([`.github/workflows/security.yml`](.github/workflows/security.yml)):

1. **RFC 7517 Public JWKS Key Discovery**:
   - Public keys are exposed at `/.well-known/jwks.json` using standard Ed25519 (`EdDSA`/`OKP`) and RSA (`RS256`) key descriptors.
2. **Deterministic Claim Tampering Defense**:
   - Every credential and proof is bound to a canonical SHA-256 digest (`RFC 8785`). Modifying any claim field (e.g., percentage, degree, income) without an authoritative re-signature causes instant mathematical verification failure.
3. **Presentation Token Integrity & JWS Validation**:
   - Proof tokens are signed with Ed25519 (`did:digiin:authority:root`). Tampered token headers, mutated payloads, or corrupted signatures are strictly rejected with `INVALID_PROOF`.
4. **Strict Audience Boundary Isolation (Replay Protection)**:
   - Proof tokens are purpose-bound and cryptographically restricted to their intended audience (e.g., `aud: "du_scholarship_portal"`). Presenting a token to an unintended verifier is blocked with `AUDIENCE_MISMATCH`.
5. **Validity Window & Expiration Enforcement**:
   - Expired timestamps are rejected immediately upon introspection with `EXPIRED`.
6. **Dynamic Cryptographic Revocation (W3C StatusList2021 / RFC 5280 CRL)**:
   - Revoked credentials propagate instantly across the federated registry. Introspecting a revoked proof returns `REVOKED` along with immutable audit metadata.
7. **Zero-Knowledge Data Minimization (0 Raw Bytes Leaked)**:
   - Zero-knowledge predicate evaluation computes salted boolean commitments (`sha256(predicate_id || is_satisfied || salt)`) and Merkle tree roots, transferring **0 bytes of raw PDFs or unblinded PII**.
8. **Synthetic Sandbox Boundaries (Zero Real PII)**:
   - All demo fixtures, unit tests, and test suites utilize demonstrably synthetic identifiers (`DIN-DEMO-001`, `9999-XXXX-XXXX`). No real citizen credentials are ever committed.

---

## 🚦 Automated Security CI Enforcement Pipeline

| Security Stage | Tool / Harness | Policy / Exit Gate |
| :--- | :--- | :--- |
| **Python Dependency Audit** | `pip-audit -r services/api/requirements.txt` | **Strict Blocking** (0 known CVEs allowed) |
| **Frontend Dependency Audit** | `npm audit --audit-level=high` | **Strict Blocking** (0 high/critical CVEs allowed) |
| **Static Code Analysis (SAST)** | `bandit -r services/api/app -ll` | **Strict Blocking** (0 High/Medium severity issues) |
| **Secret Scanning** | Automated Regex & Private Key Inspection | **Strict Blocking** (0 unencrypted keys/tokens) |
| **Threat-Model Cryptographic Suite** | `tests/test_security_threat_model.py` | **100% Pass Rate** across all 8 security gates |

---

## 📦 Dependency Pinning & Reproducibility Policy

- **Frontend (`apps/web/package.json`)**: All production dependencies and build tools are pinned to exact semver versions (`^19.2.8`, `^8.2.2`, `^7.0.2`) matching `package-lock.json`. The use of `"latest"` is strictly prohibited.
- **Backend (`services/api/pyproject.toml` & `services/api/requirements.txt`)**: Production packages are synchronized with explicit version boundaries.

---

## 🚨 Vulnerability Reporting

If you discover a security vulnerability within DigiIn, please report it via GitHub Security Advisories or contact the maintainers at `security@digiin.gov.in` (synthetic demo contact). Please do not disclose vulnerabilities publicly until a patch has been published.
