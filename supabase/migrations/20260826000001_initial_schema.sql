-- DigiIn (DigiLocker X) Initial PostgreSQL Schema Migration
-- Compatible with Supabase PostgreSQL and Render Managed PostgreSQL

-- 1. DigiIn Sovereign Accounts
CREATE TABLE IF NOT EXISTS digiin_accounts (
    id VARCHAR(80) PRIMARY KEY,
    account_id VARCHAR(80) UNIQUE NOT NULL,
    phone_number VARCHAR(40) NOT NULL,
    role VARCHAR(40) DEFAULT 'CITIZEN',
    status VARCHAR(40) DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_accounts_account_id ON digiin_accounts(account_id);
CREATE INDEX IF NOT EXISTS idx_accounts_phone_number ON digiin_accounts(phone_number);

-- 2. Identity Claims
CREATE TABLE IF NOT EXISTS identity_claims (
    id VARCHAR(80) PRIMARY KEY,
    account_id VARCHAR(80) NOT NULL REFERENCES digiin_accounts(account_id) ON DELETE CASCADE,
    claim_type VARCHAR(80) NOT NULL,
    value_reference VARCHAR(200) NOT NULL,
    verification_level INTEGER DEFAULT 0,
    source VARCHAR(140) NOT NULL,
    verified_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_id_claims_account_id ON identity_claims(account_id);
CREATE INDEX IF NOT EXISTS idx_id_claims_claim_type ON identity_claims(claim_type);

-- 3. Authentication Challenges
CREATE TABLE IF NOT EXISTS auth_challenges (
    id VARCHAR(80) PRIMARY KEY,
    account_id VARCHAR(80) NOT NULL,
    channel VARCHAR(40) DEFAULT 'SMS',
    challenge_hash VARCHAR(200) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    attempts INTEGER DEFAULT 0,
    consumed_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_auth_challenges_account_id ON auth_challenges(account_id);

-- 4. Session Tokens
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(80) PRIMARY KEY,
    account_id VARCHAR(80) NOT NULL,
    token_family VARCHAR(80) NOT NULL,
    refresh_token_hash VARCHAR(200) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_sessions_account_id ON sessions(account_id);

-- 5. Security Events
CREATE TABLE IF NOT EXISTS security_events (
    id VARCHAR(80) PRIMARY KEY,
    account_id VARCHAR(80) NOT NULL,
    event_type VARCHAR(80) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    request_id VARCHAR(80),
    metadata_json TEXT DEFAULT '{}'
);

-- 6. Sovereign Credentials (Zero-Knowledge Verifiable Credentials)
CREATE TABLE IF NOT EXISTS sovereign_credentials (
    credential_id VARCHAR(80) PRIMARY KEY,
    account_id VARCHAR(80) NOT NULL,
    credential_type VARCHAR(80) NOT NULL,
    issuer VARCHAR(140) NOT NULL,
    claims_json TEXT DEFAULT '[]',
    issued_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(40) DEFAULT 'active',
    verification_case_id VARCHAR(80)
);
CREATE INDEX IF NOT EXISTS idx_credentials_account_id ON sovereign_credentials(account_id);
CREATE INDEX IF NOT EXISTS idx_credentials_type ON sovereign_credentials(credential_type);
CREATE INDEX IF NOT EXISTS idx_credentials_status ON sovereign_credentials(status);

-- 7. Verification Gateway Requests
CREATE TABLE IF NOT EXISTS gateway_verification_requests (
    request_id VARCHAR(80) PRIMARY KEY,
    verifier_id VARCHAR(80) NOT NULL,
    account_id VARCHAR(80) NOT NULL,
    purpose VARCHAR(200) NOT NULL,
    requested_claim_types_json TEXT DEFAULT '[]',
    status VARCHAR(40) DEFAULT 'pending',
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_gateway_requests_account ON gateway_verification_requests(account_id);
CREATE INDEX IF NOT EXISTS idx_gateway_requests_verifier ON gateway_verification_requests(verifier_id);

-- 8. Verification Gateway Consents
CREATE TABLE IF NOT EXISTS gateway_consents (
    consent_id VARCHAR(80) PRIMARY KEY,
    request_id VARCHAR(80) NOT NULL REFERENCES gateway_verification_requests(request_id) ON DELETE CASCADE,
    account_id VARCHAR(80) NOT NULL,
    decision VARCHAR(40) NOT NULL,
    approved_claim_types_json TEXT DEFAULT '[]',
    granted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_gateway_consents_request ON gateway_consents(request_id);

-- 9. Citizen Wallet Documents
CREATE TABLE IF NOT EXISTS documents (
    document_id VARCHAR(80) PRIMARY KEY,
    title VARCHAR(140) NOT NULL,
    document_type VARCHAR(80) NOT NULL,
    category VARCHAR(80) NOT NULL,
    verification_status VARCHAR(40) DEFAULT 'UNVERIFIED',
    trust_level INTEGER DEFAULT 1,
    owner_account_id VARCHAR(80),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 10. Document Version Chain
CREATE TABLE IF NOT EXISTS document_versions (
    version_id VARCHAR(80) PRIMARY KEY,
    document_id VARCHAR(80) NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    status VARCHAR(40) DEFAULT 'ACTIVE',
    owner_account_id VARCHAR(80),
    object_id VARCHAR(80),
    sha256 VARCHAR(64),
    content_type VARCHAR(80),
    size_bytes INTEGER,
    processing_status VARCHAR(40),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 11. Document Background Jobs
CREATE TABLE IF NOT EXISTS document_jobs (
    job_id VARCHAR(80) PRIMARY KEY,
    document_id VARCHAR(80) NOT NULL,
    version_id VARCHAR(80) NOT NULL,
    job_type VARCHAR(80) NOT NULL,
    status VARCHAR(40) DEFAULT 'PENDING',
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    available_at TIMESTAMP WITH TIME ZONE,
    worker_id VARCHAR(80),
    result_json TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 12. Structured OCR Claims
CREATE TABLE IF NOT EXISTS document_claims (
    claim_id VARCHAR(80) PRIMARY KEY,
    document_id VARCHAR(80) NOT NULL,
    version_id VARCHAR(80) NOT NULL,
    claim_key VARCHAR(80) NOT NULL,
    claim_value VARCHAR(255) NOT NULL,
    confidence_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 13. Verifier Department Cases
CREATE TABLE IF NOT EXISTS verification_cases (
    case_id VARCHAR(80) PRIMARY KEY,
    document_id VARCHAR(80) NOT NULL,
    department VARCHAR(80) NOT NULL,
    status VARCHAR(40) DEFAULT 'PENDING',
    reviewer_id VARCHAR(80),
    decision_note TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    decided_at TIMESTAMP WITH TIME ZONE
);

-- 14. Immutable Cryptographic Audit Log
CREATE TABLE IF NOT EXISTS audit_events (
    event_id VARCHAR(80) PRIMARY KEY,
    event_type VARCHAR(80) NOT NULL,
    aggregate_id VARCHAR(80) NOT NULL,
    actor_id VARCHAR(80) NOT NULL,
    details_json TEXT DEFAULT '{}',
    prev_hash VARCHAR(64) DEFAULT '0',
    hash VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 15. Merit Records Sandbox Registry
CREATE TABLE IF NOT EXISTS merit_records (
    roll_number VARCHAR(80) PRIMARY KEY,
    candidate_name VARCHAR(140) NOT NULL,
    percentile FLOAT NOT NULL,
    passed_year INTEGER NOT NULL,
    status VARCHAR(40) DEFAULT 'VERIFIED'
);
