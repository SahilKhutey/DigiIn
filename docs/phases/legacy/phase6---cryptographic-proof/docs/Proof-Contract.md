# DigiIn Proof Contract

The proof is an issuer-signed statement about the exact claims disclosed for one verifier request.

Example logical payload:

```json
{
  "proof_id": "PRF-...",
  "issuer": "digiin",
  "audience": "department-id",
  "issued_at": 1900000000,
  "expires_at": 1900000300,
  "nonce": "request-challenge",
  "claims": {
    "income_band": "eligible"
  },
  "key_id": "issuer-key-1"
}
```

The signature is Ed25519 over canonical JSON of the complete payload.

A production deployment must publish issuer public keys through a trusted JWKS/key-discovery boundary and rotate keys without exposing private material.

Offline verification means the verifier can validate the signature and proof constraints locally once it possesses a trusted issuer public key.
