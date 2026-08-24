# DigiIn — Accessibility, Inclusivity & Low-Bandwidth Engineering

## 1. Accessibility First: WCAG 2.2 AA Compliance

Public digital services in India must be accessible to every citizen, regardless of device, physical ability, or digital literacy. DigiIn embeds accessibility directly into the core design system:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DIGIIN ACCESSIBILITY STANDARDS                         │
│                                                                             │
│  [Touch]     Minimum 48 x 48px touch targets for single-thumb mobile use   │
│  [Contrast]  4.5:1 minimum text contrast ratio (7:1 for headers)           │
│  [Status]    Icon + clear text labels (Never color-only indicators)         │
│  [Keyboard]  Full tab navigation with visible 2px solid #0052CC focus ring  │
│  [Audio]     Descriptive ARIA live regions for dynamic proof verification   │
│  [Motion]    prefers-reduced-motion CSS media query support                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Bilingual Parity: English & Hindi (`हिन्दी`)

DigiIn provides full bilingual parity across the entire citizen application journey:
- Service descriptions and estimated time savings
- Plain-language legal consent explanations
- Sharing review breakdown (Shared vs Withheld)
- Error states and recovery actions

```json
{
  "app": {
    "tagline_en": "You shouldn't have to prove the same thing five times.",
    "tagline_hi": "आपको एक ही बात पांच बार साबित नहीं करनी चाहिए।"
  }
}
```

---

## 3. Low-Bandwidth "Data Saver" Mode

For citizens on 2G/3G networks or metered data connections:
- **Zero Heavy Media**: Suppresses multi-megabyte PDF previews in favor of lightweight SVG badges.
- **Payload Compression**: Strips extraneous debug metadata, reducing JSON wire payload by **$> 90\%$**.
- **Offline Reliability**: Saves verification outcome tokens locally for offline proof of submission.
