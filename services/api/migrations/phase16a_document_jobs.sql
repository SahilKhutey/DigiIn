-- Phase 16A: Async Document Processing Pipeline Schema
-- Adds missing columns to document_jobs and creates ocr_audit_trail.
-- Safe to run multiple times (uses ALTER TABLE IF NOT EXISTS pattern via SQLite pragmas).

-- document_jobs: add Phase 16A columns (SQLite-compatible via separate ALTER statements)
ALTER TABLE document_jobs ADD COLUMN IF NOT EXISTS max_attempts INTEGER NOT NULL DEFAULT 3;
ALTER TABLE document_jobs ADD COLUMN IF NOT EXISTS available_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE document_jobs ADD COLUMN IF NOT EXISTS worker_id TEXT NULL;
ALTER TABLE document_jobs ADD COLUMN IF NOT EXISTS result_json TEXT NULL;

-- Update legacy status values to Phase 16A state machine values
UPDATE document_jobs SET status = 'QUEUED' WHERE status = 'PENDING';

-- Performance index for the job dispatcher (picks up ready jobs ordered by priority)
CREATE INDEX IF NOT EXISTS idx_document_jobs_ready
  ON document_jobs(status, available_at, priority);

CREATE INDEX IF NOT EXISTS idx_document_jobs_document
  ON document_jobs(document_id);

-- OCR Audit Trail: immutable extraction records with human-review fallback
CREATE TABLE IF NOT EXISTS ocr_audit_trail (
  id                     TEXT PRIMARY KEY,
  document_id            TEXT NOT NULL REFERENCES user_documents(id) ON DELETE CASCADE,
  job_id                 TEXT NULL,
  extraction_version     INTEGER NOT NULL DEFAULT 1,
  provider               TEXT NOT NULL DEFAULT 'LocalOCR',
  raw_extracted_json     TEXT NOT NULL DEFAULT '{}',
  structured_fields_json TEXT NOT NULL DEFAULT '{}',
  classification_type    TEXT NOT NULL DEFAULT 'OTHER',
  classification_confidence REAL NOT NULL DEFAULT 0.0,
  requires_human_review  INTEGER NOT NULL DEFAULT 0,   -- 0=false, 1=true (SQLite bool)
  human_review_reason    TEXT NULL,
  human_reviewed_at      TIMESTAMP NULL,
  human_reviewer_id      TEXT NULL,
  human_review_decision  TEXT NULL,                   -- 'APPROVED' | 'REJECTED'
  processing_duration_ms INTEGER NULL,
  created_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ocr_audit_document ON ocr_audit_trail(document_id);
CREATE INDEX IF NOT EXISTS idx_ocr_audit_job ON ocr_audit_trail(job_id);
CREATE INDEX IF NOT EXISTS idx_ocr_audit_human_review ON ocr_audit_trail(requires_human_review);
