# DigiIn Verification Gateway Contract

## Request

```json
{
  "account_id": "DIN-XXXX-XXXX-XXXX",
  "purpose": "Scholarship eligibility",
  "requested_claims": ["income_band", "domicile"]
}
```

The Account ID is a routing identifier, not an authorization credential.

## Citizen approval

The citizen sees:
- requesting department
- stated purpose
- requested claims
- credential/source backing each claim
- expiry
- approve/deny controls

The citizen may approve a subset of requested claims.

## Response

```json
{
  "valid": true,
  "request_id": "REQ-...",
  "purpose": "Scholarship eligibility",
  "claims": {
    "income_band": "eligible"
  },
  "proof": "signed-proof-reference"
}
```

The final production response must be cryptographically signed and must support independent verification.

Raw documents are not part of the normal response.
