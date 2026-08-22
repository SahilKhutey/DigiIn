# DigiLocker X — Database & Entity Specification

This document defines the relational domain models, entity relationships, PostgreSQL DDL schemas, constraints, and indexing strategy for the DigiLocker X platform.

---

## 1. Domain Entity Relationship Diagram

```
                 ┌──────────────────┐
                 │  organizations   │
                 └────────┬─────────┘
                          │ 1
                          │
                          │ has many
                          ▼
                 ┌──────────────────┐
                 │  issuers / reqs  │
                 └────────┬─────────┘
                          │ 1
                          │
                          │ issues / requests
                          ▼
┌──────────────┐ 1      * ┌──────────────────┐ 1        * ┌──────────────────────┐
│    users     ├─────────►│   credentials    ├───────────►│ verification_results │
└──────┬───────┘          └──────────────────┘            └──────────┬───────────┘
       │ 1                                                           ▲
       │                                                             │
       │ has many                                                    │ relates to
       ▼                                                             │
┌──────────────┐ 1      * ┌──────────────────┐ 1        * ┌──────────┴───────────┐
│  documents   ├─────────►│ document_versions│            │verification_requests │
└──────┬───────┘          └──────────────────┘            └──────────┬───────────┘
       │ 1                                                           │ 1
       │                                                             │
       │ verified by                                                 │ has
       ▼                                                             ▼
┌──────────────┐ 1      * ┌──────────────────┐            ┌──────────────────────┐
│ verif_cases  ├─────────►│  verif_evidence  │            │       consents       │
└──────────────┘          └──────────────────┘            └──────────────────────┘
```

---

## 2. PostgreSQL Schema DDL

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users (Citizens and Platform Identities)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(20) UNIQUE,
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(255),
    date_of_birth DATE,
    gender VARCHAR(20),
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, SUSPENDED, PENDING_VERIFICATION
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_users_phone ON users(phone_number);

-- 2. Organizations (Issuers, Requesters, Government Departments)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(64) UNIQUE NOT NULL, -- e.g. CBSE_IN, NTA_IN, IIT_BOMBAY
    type VARCHAR(32) NOT NULL,        -- ISSUER, REQUESTER, HYBRID, GOV_DEPARTMENT
    verification_authority_level INTEGER NOT NULL DEFAULT 4,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    public_key_pem TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_org_code ON organizations(code);

-- 3. Documents (Uploaded & Digital Files)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_type VARCHAR(100) NOT NULL, -- CLASS_XII, AADHAAR, DRIVING_LICENSE
    title VARCHAR(255) NOT NULL,
    source_type VARCHAR(32) NOT NULL,    -- CITIZEN_UPLOAD, ISSUER_ISSUED, DIGITIZED_LEGACY
    verification_status VARCHAR(32) NOT NULL DEFAULT 'UNVERIFIED', -- UNVERIFIED, PENDING, VERIFIED, REJECTED
    storage_uri VARCHAR(512),
    file_hash_sha256 VARCHAR(64),
    current_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_docs_user ON documents(user_id);
CREATE INDEX idx_docs_type ON documents(document_type);

-- 4. Document Versions & Correction Lineage
CREATE TABLE document_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    parent_version_id UUID REFERENCES document_versions(id),
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, SUPERSEDED, REVOKED
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    change_summary TEXT NOT NULL,
    authorized_by VARCHAR(128) NOT NULL,
    evidence_uri VARCHAR(512),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    superseded_at TIMESTAMPTZ
);
CREATE INDEX idx_doc_versions_doc ON document_versions(document_id);

-- 5. Credentials (Authoritative Claims)
CREATE TABLE credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    issuer_id UUID REFERENCES organizations(id),
    document_id UUID REFERENCES documents(id),
    credential_type VARCHAR(100) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, SUSPENDED, REVOKED, EXPIRED
    verification_level INTEGER NOT NULL DEFAULT 0, -- 0: Self, 1: OCR, 3: Officer, 4: Issuer Direct
    claims JSONB NOT NULL DEFAULT '{}'::jsonb,
    signature TEXT,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ
);
CREATE INDEX idx_cred_user ON credentials(user_id);
CREATE INDEX idx_cred_issuer ON credentials(issuer_id);
CREATE INDEX idx_cred_type ON credentials(credential_type);

-- 6. Verification Requests (Inbound Sharing & Verification Inquiries)
CREATE TABLE verification_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requester_id UUID NOT NULL REFERENCES organizations(id),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    purpose TEXT NOT NULL,
    audience VARCHAR(255) NOT NULL,
    required_credential_type VARCHAR(100) NOT NULL,
    requested_attributes JSONB NOT NULL DEFAULT '[]'::jsonb,
    minimum_verification_level INTEGER NOT NULL DEFAULT 3,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING', -- PENDING, APPROVED, REJECTED, EXPIRED, REVOKED
    nonce VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_verif_req_user ON verification_requests(user_id);
CREATE INDEX idx_verif_req_status ON verification_requests(status);

-- 7. Consents (Citizen Decision Ledger)
CREATE TABLE consents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    verification_request_id UUID NOT NULL REFERENCES verification_requests(id),
    decision VARCHAR(32) NOT NULL, -- GRANTED, DENIED, REVOKED
    disclosed_attributes JSONB NOT NULL DEFAULT '[]'::jsonb,
    granted_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_consents_req ON consents(verification_request_id);

-- 8. Verification Results & Proofs
CREATE TABLE verification_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    verification_request_id UUID NOT NULL REFERENCES verification_requests(id),
    credential_id UUID REFERENCES credentials(id),
    result VARCHAR(32) NOT NULL, -- VERIFIED, REJECTED, REQUIRES_REVIEW, ISSUER_UNAVAILABLE, NOT_FOUND
    verification_level INTEGER NOT NULL,
    proof_token TEXT NOT NULL,
    disclosed_claims JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_verif_results_req ON verification_results(verification_request_id);

-- 9. Verification Cases & Officer Queues
CREATE TABLE verification_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id),
    user_id UUID NOT NULL REFERENCES users(id),
    claimed_issuer_id UUID REFERENCES organizations(id),
    verifier_queue VARCHAR(64) NOT NULL, -- EDU_BOARD_QUEUE, TRANSPORT_QUEUE, IDENTITY_QUEUE
    automated_match_score INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(32) NOT NULL DEFAULT 'OPEN', -- OPEN, IN_REVIEW, APPROVED, REJECTED, ESCALATED
    assigned_officer_id UUID,
    officer_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    decided_at TIMESTAMPTZ
);
CREATE INDEX idx_verif_cases_queue ON verification_cases(verifier_queue);
CREATE INDEX idx_verif_cases_status ON verification_cases(status);

-- 10. Immutable Sovereign Domain Events (Audit Trail)
CREATE TABLE domain_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    aggregate_id VARCHAR(128) NOT NULL,
    actor_id VARCHAR(128) NOT NULL,
    actor_role VARCHAR(64) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_events_aggregate ON domain_events(aggregate_id);
CREATE INDEX idx_events_created ON domain_events(created_at);
```
