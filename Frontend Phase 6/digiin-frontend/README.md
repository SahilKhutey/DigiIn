# DigiIn Frontend — Phase 6: Document Verification Engine

UX4G-aligned frontend foundation for DigiIn's **Document Verification Engine & Proof Minting**.

## Phase 6 Overview

Phase 6 implements the core verification engine lifecycle:
1. **Checking Document Integrity** (SHA-256 digests and digital seals).
2. **Matching Issuing Authority** (Resolving official CBSE / UIDAI public signing keys).
3. **Checking Document Details & Predicates** (Demographic matching & Zero-Knowledge predicate assertions `percentage >= 60.0%`).
4. **Minting Signed Verifiable Proof Receipt** (RFC 7515/7519 Ed25519 verifiable credential token).

## Run Locally

```bash
python -m http.server 4178
```

Open `http://localhost:4178`.
