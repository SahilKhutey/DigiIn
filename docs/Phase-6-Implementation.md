# DigiIn Phase 6 — Cryptographic Proof, Consent & Offline Verification

## Objective

Turn the Phase 5 minimum-disclosure response into a cryptographically verifiable proof that a department can validate independently.

## Architecture

Citizen consent
→ disclosed claims
→ canonical payload
→ Ed25519 signature
→ proof envelope
→ verifier
→ signature + issuer + expiry + audience + nonce checks.

## Security invariants

1. The proof signs the exact disclosed payload.
2. Claim values are never modified after signing.
3. Proofs contain issuer, audience, issued-at and expiry.
4. A unique proof ID prevents replay tracking.
5. A nonce/challenge binds a proof to a verifier request.
6. Verification fails for altered payloads.
7. Verification fails for expired proofs.
8. Verification fails for the wrong audience.
9. Verification fails for an unknown issuer key.
10. Private signing keys never leave the issuer signing boundary.

## Proof envelope

- proof_id
- type
- issuer
- audience
- issued_at
- expires_at
- nonce
- claims
- key_id
- signature

## API target

POST /api/v1/proofs/present
POST /api/v1/proofs/verify
GET  /api/v1/issuers/{issuer_id}/keys

## Offline verification

A verifier that already has the trusted issuer public key must be able to validate:
- signature
- issuer
- audience
- expiry
- nonce/request binding
- proof structure

No raw document lookup is required for cryptographic verification.

## Exit criteria

A proof generated from an approved consent can be independently verified. Any change to claims, issuer, audience, nonce or expiry causes verification to fail.
