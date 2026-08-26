-- DigiIn (DigiLocker X) Synthetic Demonstration Seed Data
-- 100% Synthetic identities and documents for hackathon evaluation

-- 1. DigiIn Demo Accounts
INSERT INTO digiin_accounts (id, account_id, phone_number, role, status, created_at, updated_at)
VALUES
  ('acc_rahul_001', 'DIN-DEMO-001', '9876543210', 'CITIZEN', 'ACTIVE', NOW(), NOW()),
  ('acc_priya_002', 'DIN-DEMO-002', '9876500000', 'CITIZEN', 'ACTIVE', NOW(), NOW()),
  ('acc_du_001', 'ORG-DEMO-001', '9876511111', 'VERIFIER', 'ACTIVE', NOW(), NOW()),
  ('acc_cbse_001', 'ISS-DEMO-CBSE', '9876522222', 'ISSUER', 'ACTIVE', NOW(), NOW()),
  ('acc_admin_001', 'ADMIN-DEMO-01', '9876599999', 'ADMIN', 'ACTIVE', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 2. Identity Claims for Rahul Sharma
INSERT INTO identity_claims (id, account_id, claim_type, value_reference, verification_level, source, verified_at)
VALUES
  ('ic_name_001', 'DIN-DEMO-001', 'name', 'Rahul Sharma', 4, 'UIDAI_SANDBOX_EKYC', NOW()),
  ('ic_dob_001', 'DIN-DEMO-001', 'dob', '2006-05-14', 4, 'UIDAI_SANDBOX_EKYC', NOW()),
  ('ic_state_001', 'DIN-DEMO-001', 'state', 'Delhi', 4, 'UIDAI_SANDBOX_EKYC', NOW()),
  ('ic_phone_001', 'DIN-DEMO-001', 'phone', '9876543210', 4, 'TELECOM_OTP_BINDING', NOW())
ON CONFLICT (id) DO NOTHING;

-- 3. Sovereign Verifiable Credentials
INSERT INTO sovereign_credentials (credential_id, account_id, credential_type, issuer, claims_json, issued_at, expires_at, status, verification_case_id)
VALUES
  ('CRD-CBSE-XII-99214', 'DIN-DEMO-001', 'EDUCATION_RECORD', 'Central Board of Secondary Education', '[{"claim_type":"student_name","value":"Rahul Sharma","source":"CBSE_OFFICIAL_REGISTRY","verification_level":4},{"claim_type":"roll_number","value":"99214","source":"CBSE_OFFICIAL_REGISTRY","verification_level":4},{"claim_type":"passed_class_xii","value":"true","source":"CBSE_OFFICIAL_REGISTRY","verification_level":4},{"claim_type":"percentage","value":"94.2","source":"CBSE_OFFICIAL_REGISTRY","verification_level":4}]', NOW(), NULL, 'active', 'CASE-CBSE-001'),
  ('CRD-REV-INC-2026', 'DIN-DEMO-001', 'INCOME_CERTIFICATE', 'Department of Revenue', '[{"claim_type":"holder_name","value":"Rahul Sharma","source":"STATE_REVENUE_REGISTRY","verification_level":4},{"claim_type":"annual_income_inr","value":"450000","source":"STATE_REVENUE_REGISTRY","verification_level":4},{"claim_type":"income_below_8lpa","value":"true","source":"STATE_REVENUE_REGISTRY","verification_level":4}]', NOW(), NOW() + INTERVAL '365 days', 'active', 'CASE-REV-001'),
  ('CRD-REV-DOM-2026', 'DIN-DEMO-001', 'DOMICILE_CERTIFICATE', 'State District Magistrate Office', '[{"claim_type":"resident_name","value":"Rahul Sharma","source":"STATE_DOMICILE_REGISTRY","verification_level":4},{"claim_type":"domicile_state","value":"Delhi","source":"STATE_DOMICILE_REGISTRY","verification_level":4}]', NOW(), NULL, 'active', 'CASE-DOM-001')
ON CONFLICT (credential_id) DO NOTHING;

-- 4. Merit Records
INSERT INTO merit_records (roll_number, candidate_name, percentile, passed_year, status)
VALUES
  ('99214', 'Rahul Sharma', 94.2, 2026, 'VERIFIED'),
  ('88412', 'Priya Verma', 96.8, 2026, 'VERIFIED')
ON CONFLICT (roll_number) DO NOTHING;

-- 5. Wallet Documents
INSERT INTO documents (document_id, title, document_type, category, verification_status, trust_level, owner_account_id, created_at)
VALUES
  ('doc_cbse_2026_01', 'CBSE Class XII Marksheet (2026)', 'CLASS_XII', 'Education', 'VERIFIED', 4, 'DIN-DEMO-001', NOW()),
  ('doc_income_2026_01', 'Annual Income Certificate (FY 2025-26)', 'INCOME_CERTIFICATE', 'Revenue', 'VERIFIED', 4, 'DIN-DEMO-001', NOW()),
  ('doc_domicile_2026_01', 'Delhi State Domicile Certificate', 'DOMICILE_CERTIFICATE', 'General', 'VERIFIED', 4, 'DIN-DEMO-001', NOW()),
  ('doc_morth_dl_2021', 'Smart Card Driving Licence', 'DRIVING_LICENCE', 'Transport', 'VERIFIED', 4, 'DIN-DEMO-001', NOW())
ON CONFLICT (document_id) DO NOTHING;
