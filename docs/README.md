# DigiIn — Documentation Hub & Master Index

Welcome to the **DigiIn Documentation Hub**. DigiIn is a sovereign Digital Trust and Verification Infrastructure connecting citizens, authoritative credential issuers, and verifying institutions.

---

## 🧭 Navigation & Core Documents

### 🏛️ 1. Architecture & Design
- **[Master Architecture](architecture/MASTER_ARCHITECTURE.md)**: Multi-tier platform reference architecture, trust boundaries, and core invariants.
- **[Operational Flowcharts](architecture/FLOWCHARTS.md)**: 10 comprehensive Mermaid sequence and workflow flowcharts covering every system interaction.
- **[Phase Catalog](PHASE_CATALOG.md)**: Detailed breakdown and deliverables across all 36 completed phases.

### 🏆 2. Hackathon & Evidence Package
- **[Hackathon Overview](hackathon/README.md)**: Problem statement, value proposition, and key differentiators.
- **[Verification Evidence](hackathon/VERIFICATION.md)**: 7-point deterministic verification matrix, negative proof results, and Verification Lab guide (`/admin/verification-lab`).
- **[Live Demonstration Script](hackathon/DEMO.md)**: 5–7 minute dual-browser live walkthrough script (Citizen Rahul Sharma $\leftrightarrow$ National Scholarship Portal).

### 🔒 3. Security, Privacy & Compliance
- **[Security Architecture](security.md)**: Cryptographic algorithms (Ed25519, SHA-256, PBKDF2), token security, and session controls.
- **[Threat Model](THREAT-MODEL.md)**: STRIDE threat modeling and mitigation strategy.
- **[Data Classification](DATA-CLASSIFICATION.md)**: Data categorization and minimal disclosure rules.
- **[Incident Response](INCIDENT-RESPONSE.md)**: Protocols for handling security anomalies and revocations.

### 💻 4. API & Integration
- **[OpenAPI 3.0 Specification](openapi.json)**: Complete machine-readable REST API contract.
- **[Verification Gateway Contract](DigiIn-Verification-Gateway-Contract.md)**: Cryptographic proof token schemas and claim verification specs.
- **[UI & Design System](UI-UX.md)**: Component specifications, responsive patterns, and accessibility guidelines.

---

## 🧪 5. Testing & Verification

The repository contains an automated test orchestrator covering all 34 test suites with a **100% pass rate**:

```bash
python tests/run_all_tests.py
```
