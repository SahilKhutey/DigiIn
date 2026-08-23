# DigiIn Phase 2 — Real Document Ingestion & Persistent Pipeline

## Objective

Turn the existing conceptual upload/OCR/review flow into a real, persistent, provider-neutral document pipeline.

## Pipeline

Client
→ multipart upload
→ request validation
→ content hashing
→ malware scan boundary
→ object storage
→ Document + DocumentVersion persistence
→ async processing job
→ OCR/extraction
→ confidence/claims
→ verification/review case
→ audit event
→ credential issuance in later phases.

## Workstreams

### 2.1 Upload boundary
- Accept multipart files.
- Enforce configurable size limits.
- Validate extension AND MIME/content signature.
- Stream to storage; do not load unbounded files into memory.
- Compute SHA-256 while streaming.
- Reject empty/corrupt payloads.

### 2.2 Object storage
- Define provider-neutral ObjectStorage interface.
- Implement LocalObjectStorage for development.
- Reserve S3-compatible implementation for production.
- Never persist raw documents in PostgreSQL.

### 2.3 Document persistence
Introduce durable records for:
- Document
- DocumentVersion
- ProcessingJob
- DocumentClaim

Minimum invariants:
- Every version has a content hash.
- Versions are immutable.
- A superseding version points to its parent.
- Document ownership is explicit.
- Processing state is auditable.

### 2.4 Malware/OCR boundaries
Providers must be replaceable:
- MalwareScanner
- OCRProvider

Development adapters may simulate results, but the API must expose their status as simulated.

### 2.5 Async processing
Upload must return quickly with:
- document_id
- version_id
- processing_job_id
- status

Worker handles:
1. malware scan
2. metadata extraction
3. OCR
4. claim extraction
5. status transition
6. audit event

### 2.6 Security
- Never trust client MIME.
- Never expose storage filesystem paths.
- Do not use original filenames as object keys.
- Avoid logging document contents.
- Bind documents to the authenticated subject.
- Record who/what initiated processing.

## Phase 2 acceptance test

A user can upload a PDF/JPEG/PNG and receive a persistent document version. The binary is stored outside the relational database, hashed, scanned through the provider boundary, queued for processing, and eventually reaches a terminal processing state with an auditable result.

No government integration is required for Phase 2.
