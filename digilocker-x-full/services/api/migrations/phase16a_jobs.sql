CREATE TABLE IF NOT EXISTS document_jobs (
 id TEXT PRIMARY KEY,
 document_id TEXT NOT NULL,
 job_type TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'QUEUED',
 attempts INTEGER NOT NULL DEFAULT 0,
 max_attempts INTEGER NOT NULL DEFAULT 3,
 priority INTEGER NOT NULL DEFAULT 100,
 available_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
 started_at TIMESTAMP NULL,
 completed_at TIMESTAMP NULL,
 worker_id TEXT NULL,
 error_code TEXT NULL,
 error_message TEXT NULL,
 result_json TEXT NULL,
 created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
 updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_document_jobs_ready ON document_jobs(status,available_at,priority);
CREATE INDEX IF NOT EXISTS idx_document_jobs_document ON document_jobs(document_id);
