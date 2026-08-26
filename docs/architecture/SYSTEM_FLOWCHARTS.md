# DigiLocker X (DigiIn) — Master System Flowcharts & Visual Architecture

## 1. Overall Platform Topology & Layer Interactions

```mermaid
flowchart TD
    subgraph Layer1[Layer 1: Public Web & Discovery Tier]
        Landing["🏛️ Public Home: /"] --> Services["🏛️ Services Catalog: /services"]
        Landing --> TrustReg["🛡️ Accredited Issuers Registry"]
        Landing --> Auth["👤 1-Click Persona Sign-In"]
    end

    subgraph Layer2[Layer 2: Sovereign Citizen Application Tier]
        Auth --> CitizenHub["📱 Citizen Hub & Vault: /wallet"]
        CitizenHub --> ScholarshipJourney["🎓 7-Screen Scholarship Flow"]
        CitizenHub --> ConsentManager["🛡️ Consent & Revocation Manager"]
        CitizenHub --> OfflineScanner["📷 Offline QR Proof Scanner"]
    end

    subgraph Layer3[Layer 3: Relying Party & Institutional Verifier Tier]
        Services --> ServicePortal["🏫 Delhi University Admission Portal"]
        ServicePortal --> ScholarshipJourney
        VerifierConsole["🏢 Verifier Portal / Console"] --> ProofVerifier["🔍 Proof Verification Engine"]
    end

    subgraph Layer4[Layer 4: Core Trust & Cryptographic Verification Engine]
        ScholarshipJourney --> ZkEngine["🔒 ZK Range & Predicate Evaluator"]
        ScholarshipJourney --> Ed25519Minter["✍️ Ed25519 Proof Signer (RFC 8785 JCS)"]
        ProofVerifier --> Ed25519Verifier["✅ Asymmetric Signature & Digest Validator"]
        ProofVerifier --> RevocationRegistry["🚫 Real-Time Revocation Registry Check"]
    end

    subgraph Layer5[Layer 5: Asynchronous Document Processing Pipeline]
        CitizenHub --> JobQueue["⚡ Priority Job Queue (DLQ Engine)"]
        JobQueue --> WorkerNode["⚙️ Async Worker (services/worker)"]
        WorkerNode --> Pipeline["7-Stage Pipeline (Scan -> OCR -> Extract -> Match)"]
        Pipeline --> HumanReview["👨‍💼 Issuer Officer Review (if confidence < 85%)"]
    end

    subgraph Layer6[Layer 6: Immutable Audit & Storage Tier]
        Ed25519Minter --> AuditLedger["⛓️ SHA-256 Hash-Chained Audit Ledger"]
        ProofVerifier --> AuditLedger
        HumanReview --> AuditLedger
        AuditLedger --> RelationalDB[("🗄️ PostgreSQL / SQLite Database")]
    end
```

---

## 2. Flowchart 1: Flagship Zero-Upload Scholarship Journey (7-Screen Sequence)

```mermaid
sequenceDiagram
    autonumber
    actor Citizen as Citizen (Rahul Sharma)
    participant Web as DigiIn Web App
    participant API as Public Service Gateway
    participant Vault as Sovereign Vault Engine
    participant Crypto as Ed25519 / RFC 8785 Signer
    actor Verifier as Delhi University Verifier

    Citizen->>Web: 1. Click "Apply with DigiIn" (Merit Scholarship)
    Web->>API: POST /public-service/scholarship/apply
    API->>Vault: Locate Verified Credentials for DIN-DEMO-001
    Vault-->>API: Found: Identity, Domicile, Income, CBSE Class XII
    API-->>Web: Return 4 Verified Claims & Pre-Filled Application

    Citizen->>Web: 2. Proceed to Signature Sharing Review
    Web->>Web: Render Sharing Screen: Shared Predicates (Green) vs Withheld PII (Red ✕)
    Note over Web: 🔒 ZERO Raw PDF / Aadhaar Uploaded (0 Bytes)

    Citizen->>Web: 3. Approve Purpose-Bound Consent
    Web->>API: POST /public-service/scholarship/{id}/consent-and-submit
    API->>Crypto: Canonicalize Consented Claims (RFC 8785)
    Crypto->>Crypto: Compute SHA-256 Digest & Sign with DigiIn Ed25519 Key
    Crypto-->>API: Generated Proof Token (DGI-PRF-2026-1042)
    API-->>Web: Return Submission Receipt (Ref: DGI-SCH-2026-1042)

    Citizen->>Web: 4. Open Proof in Verifier Portal
    Web->>Verifier: Present Proof Token / QR Code
    Verifier->>API: Verify Proof Integrity
    API-->>Verifier: Result: ✓ VERIFIED (100% Cryptographic Certainty)
```

---

## 3. Flowchart 2: Asynchronous Document Processing Pipeline & Human Fallback

```mermaid
flowchart TD
    Start([Citizen Uploads Document]) --> Queue[State: QUEUED in Priority Job Queue]
    Queue --> Worker[Async Background Worker Picks Job]
    
    Worker --> Stage1[1. MALWARE_SCAN: ClamAV / YARA Signature Check]
    Stage1 -- Infected --> FailInfected[Mark FAILED -> Alert Security]
    Stage1 -- Clean --> Stage2[2. OCR_PROCESSING: Text & Layout Extraction]
    
    Stage2 --> Stage3[3. CLASSIFICATION: Document Type Recognition]
    Stage3 --> Stage4[4. FIELD_EXTRACTION: Extract Roll No, DOB, Marks, Name]
    
    Stage4 --> Stage5[5. DUPLICATE_CHECK: SHA-256 Perceptual Hash Check]
    Stage5 -- Duplicate --> FailDupe[Mark FAILED -> Duplicate Detected]
    Stage5 -- Unique --> Stage6[6. ISSUER_LOOKUP: National Issuer Registry Check]
    
    Stage6 --> Stage7{7. MATCHING & CONFIDENCE SCORE}
    Stage7 -- Confidence >= 85% --> AutoVerify[Auto-Verified -> Ed25519 Mint Credential]
    Stage7 -- Confidence < 85% --> HumanQueue[Route to Government Officer Review Queue]
    
    HumanQueue --> OfficerReview[Officer Inspects Discrepancy Side-by-Side]
    OfficerReview -- Officer Approves --> AutoVerify
    OfficerReview -- Officer Rejects --> RejectDoc[Mark REJECTED with Detailed Audit Reason]
    
    AutoVerify --> SuccessState[State: SUCCEEDED -> Sovereign Vault Updated]
```

---

## 4. Flowchart 3: Cryptographic Proof Minting & Negative Proof Defense (Tamper Attack)

```mermaid
sequenceDiagram
    autonumber
    actor Attacker as Attacker / Tampering Simulation
    participant Portal as Public Verification Portal
    participant Engine as Verification Engine
    participant Crypto as Ed25519 / RFC 8785 Validator
    participant Registry as Issuer Trust & Revocation Registry

    Note over Portal: Scenario A: Authentic Proof Verification
    Portal->>Engine: Submit Proof Token (income_eligible: true)
    Engine->>Crypto: Verify Ed25519 Signature against Digest
    Crypto-->>Engine: Signature Valid ✓
    Engine->>Registry: Verify Expiration ($TTL < 24h$) & Revocation Status
    Registry-->>Engine: Not Revoked & Active ✓
    Engine-->>Portal: 🟢 Status: VERIFIED

    Note over Portal: Scenario B: Tampered Claim Attack
    Attacker->>Portal: Injects Tampered Payload (income_eligible: false)
    Portal->>Engine: Submit Tampered Proof
    Engine->>Crypto: Compute RFC 8785 Digest of Tampered Claims
    Crypto->>Crypto: Compare Computed Digest against Signed Digest
    Crypto-->>Engine: ❌ Digest Mismatch Error
    Engine-->>Portal: 🔴 Status: SIGNATURE INVALID ✕ (Tamper Caught Instantly)
```

---

## 5. Flowchart 4: Attribute-Based Access Control (ABAC) & Zero-Knowledge Predicate Engine

```mermaid
flowchart TD
    Request([Incoming Data Access Request]) --> ExtractContext[Extract Subject, Resource, Action & Environment]
    
    ExtractContext --> CheckPolicy{ABAC Policy Engine Evaluation}
    CheckPolicy -- Violates Role / Time / Purpose --> DenyAccess[🚫 403 Forbidden: Policy Violation]
    
    CheckPolicy -- Policy Passed --> CheckDisclosureType{Is Disclosure Full or ZK Predicate?}
    
    CheckDisclosureType -- ZK Range Predicate --> ZkEval[Evaluate Predicate: income < 250000 -> Boolean]
    ZkEval --> MaskValue[Mask Exact Salary Amount -> Return 'income_eligible: true']
    
    CheckDisclosureType -- Minimal Field --> StripPii[Strip Non-Consented Fields (Aadhaar, Phone, Raw Scans)]
    
    MaskValue --> SignPayload[Ed25519 Sign Minimal Payload]
    StripPii --> SignPayload
    
    SignPayload --> Output([Return Zero-PII Cryptographic Assertion])
```

---

## 6. Flowchart 5: Immutable Hash-Chained Audit Ledger ($H(E_n \parallel H_{n-1})$)

```mermaid
flowchart LR
    subgraph Block0[Genesis Block: Block 0]
        H0["Hash 0: Genesis SHA-256"]
        E0["Event 0: System Init"]
    end

    subgraph Block1[Block 1: Credential Issuance]
        H1["Hash 1: SHA-256(Event 1 || Hash 0)"]
        E1["Event 1: CBSE Class XII Minted"]
    end

    subgraph Block2[Block 2: Consent Granted]
        H2["Hash 2: SHA-256(Event 2 || Hash 1)"]
        E2["Event 2: Citizen Grants Consent to DU"]
    end

    subgraph Block3[Block 3: Proof Verified]
        H3["Hash 3: SHA-256(Event 3 || Hash 2)"]
        E3["Event 3: Proof Verified by Verifier"]
    end

    H0 --> H1 --> H2 --> H3

    style Block0 fill:#f1f5f9,stroke:#64748b
    style Block1 fill:#e0f2fe,stroke:#0284c7
    style Block2 fill:#ecfdf5,stroke:#10b981
    style Block3 fill:#fef3c7,stroke:#f59e0b
```

---

## 7. Flowchart 6: Cloud Deployment Topology & Render Sandbox Architecture

```mermaid
flowchart TD
    Internet([Public Internet / Hackathon Jury]) --> CloudDNS["Public HTTPS URL: https://digiin-web.onrender.com"]
    
    subgraph RenderPlatform[Render Cloud Infrastructure]
        CloudDNS --> WebService["digiin-web (Vite / React Static SPA)"]
        
        WebService -- "/api/v1/* (VITE_API_BASE_URL)" --> ApiService["digiin-api (FastAPI / Python 3.12)"]
        
        ApiService --> WorkerService["digiin-worker (Background Job Worker)"]
        
        ApiService -- "DIGIIN_DATABASE_URL" --> PostgresDB[("digiin-db (PostgreSQL)") ]
        WorkerService -- "DIGIIN_DATABASE_URL" --> PostgresDB
        
        subgraph SandboxLayer[Deterministic Sandbox Mock Layer]
            ApiService --> MockAuth["Demo Auth (1-Click Personas)"]
            ApiService --> MockKYC["Demo KYC (KYC-DEMO-001)"]
            ApiService --> MockGov["Demo Registries (CBSE, Revenue, Transport)"]
            ApiService --> MockNotif["Demo Notifications (In-App)"]
        end
    end
```
