# DigiIn — Master Demonstration Guide & 7-Screen Flagship Journey

## 1. The 7 Flagship Citizen Screens

The core submission demonstrates the complete scholarship application journey through 7 clean, accessible screens:

```
[Screen 01: Landing] ──> [Screen 02: Overview] ──> [Screen 03: Discovery] ──> [Screen 04: Status]
                                                                                     │
[Screen 07: Success] <── [Screen 06: Ready]    <── [Screen 05: SHARING REVIEW] <───┘
```

### Screen 01 — Landing Screen
- **Header**: `DigiIn (डिजिलॉकर एक्स)`
- **Headline**: *"Apply for services without repeatedly submitting documents. Your verified information stays under your control."*
- **Primary Action**: `[ Apply for a Scholarship ]`
- **Language Switch**: `English | हिन्दी`

### Screen 02 — Service Overview
- **Title**: `Scholarship Application — University of Delhi`
- **Requirement Summary**: *"You'll need: Identity, Domicile, Income eligibility, Education. DigiIn can provide these from your verified information."*
- **Estimated Time**: `~5 minutes` (vs 45 min traditional)
- **Action**: `[ Continue with DigiIn ]`

### Screen 03 — DigiIn Discovery
- **Headline**: *"Use your DigiIn information"*
- **Status**: *"We found 4 verified items that can help complete this application."*
- **Found Credentials**: `✓ Identity`, `✓ Domicile`, `✓ Income`, `✓ Education`
- **Action**: `[ Review Information ]`

### Screen 04 — Verification Status Detail
- **Card**: `CBSE Higher Secondary Education`
- **Issuer**: `DigiIn Demo Verified Issuer (ISSUER-DEMO-001)`
- **Last Verified**: `24 Aug 2026`
- **Credential Status**: `Active (Level 4 Sovereign Verified)`

### Screen 05 — The Signature "Sharing Review" Screen
- **Title**: `Sharing Review — What is shared vs What is kept private`
- **Requesting Entity**: `University Scholarship Service (ORG-DEMO-001)`
- **Shared with Institution**:
  - `✓ Full Name: Rahul Sharma`
  - `✓ State Domicile: Chhattisgarh (Verified)`
  - `✓ Income Requirement: Eligible (< 2.5L Threshold)`
  - `✓ Education Qualification: Class XII Passed (94.2% Marks)`
- **Not Shared (Kept Private in Your Vault)**:
  - `• Original document files (0 bytes transferred)`
  - `• Aadhaar number (Strictly redacted)`
  - `• Exact salary & tax return figures`
  - `• Full residential address`
- **Purpose**: `Scholarship Eligibility Determination`
- **Access Expires**: `24 hours after approval`
- **Actions**: `[ Approve & Continue ]` | `[ Don't Share ]`

### Screen 06 — Submission Readiness
- **Summary**: `Your application is ready: 4 verified details, 1 consent, 1 signed verification proof. No document upload required.`
- **Action**: `[ Submit Application ]`

### Screen 07 — Success & Proof Receipt
- **Headline**: `✓ Application Submitted`
- **Reference**: `DGI-SCH-2026-1042`
- **Comparison Summary**:
  - `Documents uploaded: 0`
  - `Manual verification required: No`
  - `Verification status: Cryptographically Verified ✓`
- **Action**: `[ View Verification Proof ]`

---

## 2. Robust Error States Handled

DigiIn includes first-class user interfaces for five operational failure conditions:

1. **Credential Expired**: *"This information needs to be verified again. [ Re-verify ]"*
2. **Consent Denied**: *"You chose not to share this information. No information was sent."*
3. **Verification Failure**: *"We couldn't verify this proof. No application data was changed."*
4. **Network Failure / Offline**: *"You're offline. Your application hasn't been submitted. [ Retry ]"*
5. **Provider Unavailable**: *"Verification service is temporarily unavailable. Your information is safe; we'll retry automatically."*

---

## 3. Negative Proof Attack Demonstration (`/demo/verification`)

1. Load authentic proof `PRF-DEMO-1042` $\rightarrow$ Status: `VERIFIED ✓`.
2. Click `[ Tamper with Claim ]` (toggle `income_eligible: true` to `false`).
3. Immediate cryptographic rejection $\rightarrow$ `SIGNATURE INVALID ✗: Proof digest altered after signing.`
