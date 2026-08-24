# DigiIn — Before vs After: Prototype-Flow Comparison

## 1. The Workflow Comparison

The following table contrasts the traditional Indian public service application process with the DigiIn prototype experience:

```
┌──────────────────────────────────────┬──────────────────────────────────────┐
│       TRADITIONAL SERVICE FLOW       │        DIGIIN PROTOTYPE FLOW         │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 1. Choose service on portal          │ 1. Choose service on portal          │
│ 2. Create local username & password  │ 2. One-click passwordless login      │
│ 3. Re-type name, DOB, state, parent  │ 3. Click "Use My Verified DigiIn"    │
│ 4. Scan physical Class XII marksheet │ 4. Auto-discover verified credentials│
│ 5. Scan physical Domicile certificate│ 5. Review Sharing Screen (0 raw PII) │
│ 6. Scan physical Income certificate  │ 6. One-click purpose-bound consent   │
│ 7. Upload 4 PDF scans (repeatedly)   │ 7. Ed25519 proof minted in 2 ms      │
│ 8. Submit and wait 4-6 weeks for     │ 8. Instant submission receipt        │
│    manual departmental review        │ 9. Institution verifies proof instantly│
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 2. Key Metrics & Value Proposition

| Dimension | Traditional Flow | DigiIn Prototype Flow | Impact |
|---|---|---|---|
| **Raw Documents Uploaded** | 4 files per application | **0 files** | Eliminates storage liability and scan failures |
| **Sensitive PII Disclosed** | Full Aadhaar, full tax form, full address | **Minimal boolean predicates only** | Prevents mass identity theft and honeypots |
| **Application Completion Time** | ~45 minutes | **~2 minutes** | 95% reduction in citizen cognitive load |
| **Institutional Verification** | Manual human review (3–6 weeks) | **Cryptographic check (< 5 ms)** | Instant mathematical trust |
| **Low-Bandwidth Mobile Usability** | High failure rate (> 15 MB upload) | **Data Saver Mode (< 10 KB payload)** | Highly accessible over 2G/3G connections |
| **Citizen Consent Control** | Broad, indefinite data capture | **Purpose-bound, 24h expiration** | Citizen retains sovereign data ownership |

> *Note: Metrics represent prototype-flow comparisons and latency benchmarks evaluated in the DigiIn test harness.*
