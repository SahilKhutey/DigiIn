# DigiIn — Phase 27: Trust Network Expansion & Ecosystem Operations

Trust federations, institutional onboarding readiness scoring, issuer/verifier accreditation, multi-tier assurance framework (A1-A4), multi-factor trust policies, composite and derived claims, zero-PII claim catalog, selective disclosure, governance with separation of duties, and fraud intelligence with automated anomaly throttling.

## Key Subsystems

1. **Trust Federation Manager (`FederationManager`, `OrganizationReadinessScorer`)**:
   - Manages multi-organization federations, memberships, and 6-dimension institutional readiness scoring.
2. **Accreditation Engine (`AccreditationEngine`)**:
   - Governs Issuer & Verifier accreditation across 4 assurance levels (`A1_BASIC` $\rightarrow$ `A4_REGULATED`) and organizational trust states (`TRUSTED`, `MONITORED`, `RESTRICTED`, `SUSPENDED`).
3. **Multi-Factor Trust Policy Engine (`TrustPolicyEngine`)**:
   - Evaluates Subject, Verifier, Claim, Purpose, Assurance, Consent, and Trust Relationship to return definitive `ALLOW` / `DENY` decisions.
4. **Multi-Issuer & Derived Claims Engine (`CompositeClaimEngine`)**:
   - Evaluates composite qualification rules with transparent decision reasoning.
5. **Zero-PII Claim Discovery Catalog (`ClaimCatalog`)**:
   - Enables verifiers to discover available trust claims across domains (`EDUCATION`, `IDENTITY`, `LICENSING`, `EMPLOYMENT`) without exposing citizen data.
6. **Selective Disclosure & Multi-Claim Presentation (`SelectiveDisclosureEngine`, `MultiClaimPresentationManager`)**:
   - Discloses only requested attributes and packages multi-claim presentation bundles.
7. **Network Governance & Ecosystem Analytics (`NetworkGovernanceEngine`, `NetworkAnalyticsService`)**:
   - Multi-role governance decision engine with separation of duties (`NETWORK_ADMIN`, `TRUST_ADMIN`, `SECURITY_ADMIN`, `PRIVACY_ADMIN`, `ACCREDITATION_REVIEWER`) and operational telemetry.
8. **Fraud & Abuse Intelligence (`FraudAbuseIntelligence`)**:
   - Tracks request velocity spikes and subject probes with automated throttling transitions (`NORMAL` $\rightarrow$ `THROTTLED` $\rightarrow$ `SUSPENDED`).

## Run with Docker

```bash
docker compose up -d
```
