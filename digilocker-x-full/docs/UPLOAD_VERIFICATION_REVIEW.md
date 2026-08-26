# Upload → Verification → Review

UNVERIFIED → PENDING_REVIEW → VERIFIED
                         ├→ REJECTED
                         └→ CORRECTION_REQUIRED → resubmission → PENDING_REVIEW

Upload: POST /api/v1/documents/upload
Queue: GET /api/v1/review/documents
Detail: GET /api/v1/review/documents/{document_id}
Decision: POST /api/v1/review/documents/{document_id}/decision

Decisions: APPROVE, REJECT, REQUEST_CORRECTION.
Approved self-uploaded documents become level-3 GOV_REVIEW credentials in this development foundation.
Production must add malware scanning, content sniffing, encrypted object storage, signed URLs, immutable audit, KMS/HSM signing, retention controls, and explicit government authority.
