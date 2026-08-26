# Phase 16A — Async Document Processing

Pipeline:
UPLOAD → QUEUED → MALWARE_SCAN → OCR → CLASSIFY → EXTRACT → DUPLICATE_CHECK → ISSUER_LOOKUP → VERIFICATION → REVIEW/VERIFIED

Implemented:
- provider-neutral job types and states
- development queue API
- retry contract
- worker contract
- database migration
- operational separation between upload and processing

Production requirements:
- durable broker
- atomic job claiming
- visibility timeout
- exponential backoff
- dead-letter queue
- idempotency keys
- worker authentication
- persistent job state
- audit events
- monitoring/metrics
- malware scanning
- OCR/provider adapters

Acceptance:
1. Upload returns without waiting for processing.
2. Processing is independently observable.
3. Failed jobs can retry.
4. Original documents remain immutable.
5. Downstream failures cannot corrupt document state.
