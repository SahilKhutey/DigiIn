# DigiIn — Accessibility, Bilingual Parity & Low-Bandwidth "Data Saver"

## 1. Indian Public-Service Accessibility (WCAG 2.2 AA)

Public services in India serve a diverse population with varied digital literacy, devices, and connection speeds. DigiIn prioritizes inclusion across all user interfaces:

### Accessibility Checklist:
1. **Large Touch Targets**: All actionable buttons and checkboxes have a minimum touch target of $48 \times 48\text{px}$ for easy single-handed mobile thumb operation.
2. **High Contrast Ratio**: Complies with WCAG 2.2 AA standards with a minimum contrast ratio of $4.5:1$ for normal body text and $7:1$ for headers.
3. **No Color-Only State Indicators**: Statuses always combine distinct icons and clear text labels (e.g. `[✓ Verified]`, `[✗ Invalid]`), never relying solely on color hue.
4. **Full Keyboard & Screen-Reader Support**: Semantic HTML, visible focus rings (`2px solid #0052CC`), and descriptive `aria-live` and `aria-describedby` announcements for dynamic proof verification updates.

---

## 2. Bilingual Parity: English & Hindi (`हिन्दी`)

DigiIn does not rely on superficial machine translation of navigation menus. It implements deep localization across:
- Plain-language legal consent explanations
- Educational requirements and scholarship criteria
- Cryptographic verification error descriptions
- Status badges and confirmation receipts

```json
{
  "sharing_review": {
    "title_en": "Sharing Review — What is shared vs What is kept private",
    "title_hi": "साझाकरण समीक्षा — क्या साझा किया गया और क्या गोपनीय रखा गया",
    "withheld_label_en": "Kept private in your vault (0 bytes transferred)",
    "withheld_label_hi": "आपकी तिजोरी में सुरक्षित (कोई डेटा स्थानांतरित नहीं)"
  }
}
```

---

## 3. Low-Bandwidth "Data Saver" Engine

For citizens accessing public services on 2G/3G connections or restricted mobile data packs, DigiIn provides a dedicated **Data Saver Mode**:

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚡ Data Saver is on. DigiIn will use less data.                │
└─────────────────────────────────────────────────────────────────┘
```

### Technical Optimizations in Data Saver Mode:
1. **Zero Heavy Binary Transfers**: Disables rich PDF previews and renders lightweight SVG/text claim summaries.
2. **Compressed JSON Payload Envelopes**: Strips extraneous debug metadata, achieving $\ge 60\%$ byte-size reduction on mobile networks.
3. **Skeleton Loading & Optimistic UI**: Replaces heavy spinner animations with lightweight CSS skeleton pulses.
4. **Retry-Safe Idempotent Requests**: Queues offline consent actions and replays them automatically with `Idempotency-Key` headers when network connectivity resumes.
5. **Offline-Readable Verification Receipts**: Stores compact verification outcome tokens locally in `localStorage` for offline display.
