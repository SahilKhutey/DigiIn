# DigiLocker X (DigiIn) — Master Hackathon Demonstration Script

## Overview
This script outlines the official **3-Browser Flagship Walkthrough** for live presentations, jury evaluations, and judge walk-throughs. It demonstrates sovereign citizen data ownership, purpose-bound consent, minimal selective disclosure, and the cryptographic negative proof verification lab.

---

## 🎭 Demonstration Personas & Setup

```
Browser A [Citizen]:       Rahul Sharma (ID: DGI-7K4M-X9P2-2026) — Sovereign Citizen Holder
Browser B [Institution]:   National Scholarship Portal / University of Delhi — Relying Party
Browser C [Verifier Lab]:  DigiIn Cryptographic Negative Proof & Security Lab — Jury Inspect Surface
```

---

## 🎬 Act 1: The Citizen Perspective (Browser A)

### Step 1.1: Sovereign Login & Credential Wallet
1. Navigate to the Citizen Portal (`apps/web`).
2. Log in as `Rahul Sharma` (`DGI-7K4M-X9P2-2026`).
3. View the **Credential Wallet**:
   - **Class XII Marksheet** (CBSE — Level 4 Verified)
   - **Domicile Certificate** (Chhattisgarh Revenue Authority — Level 4 Verified)
   - **Income Certificate** (Revenue Department — Level 4 Verified)
4. *Key Message to Jury*: *"All credentials in the wallet represent authoritative, verified claims — not uploaded scans stored in plain text."*

### Step 1.2: Incoming Verification Request Inbox
1. Open the **Request Inbox**.
2. Inspect the pending query from **National Scholarship Portal**:
   - Purpose: `Merit-cum-Means Scholarship Eligibility Check`
   - Requested Claims: `degree == "B.Tech"`, `passing_year == 2026`, `income_eligible == true`
3. Notice that raw Aadhaar, PAN, and full residential addresses are **NOT** requested.

### Step 1.3: Purpose-Bound Consent & Proof Granting
1. Review the consent terms: validity window (15 minutes), purpose limitation, single-use audience constraint.
2. Click **Approve & Sign Proof**.
3. DigiIn generates an **Ed25519 Signed Verification Proof** with minimal selective disclosure.

---

## 🏛️ Act 2: The Institution Perspective (Browser B)

### Step 2.1: Request Initiation
1. Open the Requester Portal (`apps/verifier-console`).
2. Select candidate `DGI-7K4M-X9P2-2026` for the Scholarship program.
3. Submit the claim verification query with strict purpose parameters.

### Step 2.2: Cryptographic Proof Reception & Validation
1. Receive the incoming signed proof payload from Browser A.
2. Click **Verify Cryptographic Claims**.
3. View the Verification Outcome:
   - **Signature Valid**: `True` (Ed25519 verified against DigiIn Root JWKS)
   - **Issuer Trusted**: `True` (Authority registered in Sovereign Trust Registry)
   - **Expiry Valid**: `True` (Within 15-minute validity window)
   - **Disclosed Claims**: `{"income_eligible": true, "degree": "B.Tech", "passing_year": 2026}`
4. *Key Message to Jury*: *"The institution verified scholarship eligibility with mathematical certainty without ever touching or storing Rahul's raw tax forms or identity documents."*

---

## 🔬 Act 3: The Negative Proof Verification Lab (Browser C)

The Verification Lab proves that security and trust are mathematical invariants, not optimistic UI assumptions.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DIGIIN VERIFICATION LAB (LIVE)                        │
├───────┬───────────────────────────────┬───────────────────┬─────────────────┤
│ Test  │ Scenario Tested               │ Expected Outcome  │ Security Reason │
├───────┼───────────────────────────────┼───────────────────┼─────────────────┤
│ TC-01 │ Authentic Valid Credential    │ VERIFIED (PASS)   │ 100% Integrity  │
│ TC-02 │ Tampered Marksheet Score      │ INVALID (REJECT)  │ Digest Mismatch │
│ TC-03 │ Rogue / Fake Issuer DID       │ UNTRUSTED (REJECT)│ Trust Registry  │
│ TC-04 │ Revoked Domicile Credential   │ REVOKED (REJECT)  │ Instant Revoke  │
│ TC-05 │ Expired Scholarship Token     │ EXPIRED (REJECT)  │ Validity Window │
└───────┴───────────────────────────────┴───────────────────┴─────────────────┘
```

### Live Lab Demonstrations:
1. **TC-01 (Valid)**: Load authentic proof $\rightarrow$ Status: `VERIFIED ✓`.
2. **TC-02 (Tampered)**: Modify `score_bracket` from `">=90%"` to `"100% TOPPER"` $\rightarrow$ Status: `INVALID ✗` (`DIGEST_INTEGRITY_CHECK`).
3. **TC-03 (Untrusted Issuer)**: Change issuer identifier to `did:fake:unauthorized` $\rightarrow$ Status: `UNTRUSTED ✗` (`ISSUER_TRUST_CHECK`).
4. **TC-04 (Revoked)**: Query revoked credential certificate $\rightarrow$ Status: `REVOKED ✗` (`REVOCATION_CHECK`).
5. **TC-05 (Expired)**: Evaluate expired timestamp $\rightarrow$ Status: `EXPIRED ✗` (`EXPIRATION_CHECK`).

---

## 🏁 Live Terminal Showcase Command

To run the automated console demonstration covering all three acts in real time:

```powershell
python scripts/hackathon_showcase.py
```
