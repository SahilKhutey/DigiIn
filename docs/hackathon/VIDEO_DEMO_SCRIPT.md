# DigiIn — 3-Minute Hackathon Submission Video Storyboard

## Overview
This storyboard guides the recording of the official **3-minute submission video** for **Build What Moves India**. It emphasizes the citizen problem, the elegant service-first solution, the institutional perspective, and the cryptographic evidence.

---

## ⏱️ Video Timeline (Total Runtime: 3:00)

```
0:00 ─── 0:20 ─── 1:30 ─── 2:00 ─── 2:30 ─── 3:00
 │         │         │         │         │      │
 └─PROBLEM─┴─CITIZEN─┴─INSTIT.─┴─SECURITY┴─WHY──┘
```

---

### Segment 1: The Problem (0:00 – 0:20)
- **Visual**: Show a citizen struggling with 4 different government portal tabs, repeatedly uploading the same Aadhaar scan, Class XII marksheet PDF, and income certificate.
- **Voiceover**: *"Why does an Indian citizen have to prove the same thing five times? Every college application, scholarship portal, and government scheme asks you to upload the exact same document scans again and again. It wastes hours, leaks sensitive Aadhaar scans into dozens of databases, and creates months of manual verification backlogs."*

---

### Segment 2: The DigiIn Citizen Flow (0:20 – 1:30)
- **Visual**: Open DigiIn mobile view ($360 \times 800$) as citizen **Rahul Sharma**.
- **Actions**:
  1. Click `[ Start Service ]` $\rightarrow$ Select `Scholarship Application (University of Delhi)`.
  2. Click `[ Use My Verified DigiIn Information ]`.
  3. Show the **Signature Sharing Review Screen**:
     - Highlight: `Shared with Institution` (*Name, Domicile: Chhattisgarh, Income: Eligible, XII Marksheet: 94.2%*).
     - Highlight: `Not Shared / Private` (*Aadhaar redacted, 0 bytes raw PDF transferred, 24h validity*).
  4. Toggle `[ हिन्दी / English ]` to demonstrate full bilingual parity.
  5. Click `[ Allow & Submit Application ]`.
  6. Instant confirmation receipt: *"Application Submitted in 2 minutes!"*
- **Voiceover**: *"With DigiIn, you verify once and reuse forever. When applying for a scholarship, DigiIn discovers your verified credentials. The signature Sharing Review screen clearly shows what is shared and what is kept private. In one tap, an Ed25519 cryptographic proof is minted with zero raw document transfer."*

---

### Segment 3: The Institutional Verification View (1:30 – 2:00)
- **Visual**: Switch to **Requester Console** (University of Delhi Scholarship Officer).
- **Actions**:
  1. Open applicant `Rahul Sharma`.
  2. View verified predicate status: `Identity ✓`, `Income Eligible ✓`, `Domicile ✓`, `Class XII 94.2% ✓`.
  3. Click `[ View Cryptographic Details ]` to reveal the valid Ed25519 signature and RFC 8785 canonical digest.
- **Voiceover**: *"On the institution side, the university gets instant mathematical verification. They don't have to download, store, or manually inspect a single PDF file. Zero storage liability, 100% certainty."*

---

### Segment 4: The Negative Proof & Tamper Defense (2:00 – 2:30)
- **Visual**: Open the **Verification Lab** (`/demo/verification`).
- **Actions**:
  1. Show authentic proof $\rightarrow$ Status: `VERIFIED ✓`.
  2. Click `[ Tamper with Claim ]`: Alter `income_eligible` from `true` to `false` or change marksheet score.
  3. Re-verify $\rightarrow$ Status flashes `INVALID ✗` (`DIGEST_INTEGRITY_CHECK failed`).
- **Voiceover**: *"Security isn't a promise; it's math. In our Verification Lab, if an attacker tampers with even a single bit of the claim data, DigiIn catches it instantly and rejects the forged proof."*

---

### Segment 5: Why It Matters & Conclusion (2:30 – 3:00)
- **Visual**: Return to the clean home screen showing Data Saver mode active.
- **Voiceover**: *"DigiIn is designed for India: fully bilingual, accessible, low-bandwidth ready, and built to make public services dramatically simpler. Stop submitting the same documents again and again. DigiIn verifies the claim, protects the citizen, and powers the service. Thank you."*
