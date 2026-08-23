"""
DigiIn Performance & Scalability — Resumable Chunked Direct Upload Manager
Handles multi-part upload sessions, chunk assembly, and SHA-256 integrity validation for large documentary evidence.
"""

from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass, field


@dataclass
class UploadSession:
    session_id: str
    document_id: str
    total_size_bytes: int
    chunk_size_bytes: int
    expected_chunks: int
    received_chunks: dict[int, bytes] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    assembled_sha256: str | None = None

class ChunkedUploadManager:
    def __init__(self, chunk_size_bytes: int = 1024 * 1024):  # 1MB chunks
        self.chunk_size_bytes = chunk_size_bytes
        self._sessions: dict[str, UploadSession] = {}

    def initiate_upload_session(self, document_id: str, total_size_bytes: int) -> UploadSession:
        sid = f"upl_{secrets.token_hex(8)}"
        expected_chunks = (total_size_bytes + self.chunk_size_bytes - 1) // self.chunk_size_bytes
        session = UploadSession(
            session_id=sid,
            document_id=document_id,
            total_size_bytes=total_size_bytes,
            chunk_size_bytes=self.chunk_size_bytes,
            expected_chunks=expected_chunks
        )
        self._sessions[sid] = session
        return session

    def upload_chunk(self, session_id: str, chunk_index: int, chunk_data: bytes) -> tuple[bool, str, UploadSession]:
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError("UPLOAD_SESSION_NOT_FOUND")

        session.received_chunks[chunk_index] = chunk_data
        if len(session.received_chunks) == session.expected_chunks:
            # Assemble all chunks in order
            assembled = b"".join(session.received_chunks[i] for i in range(session.expected_chunks))
            session.assembled_sha256 = hashlib.sha256(assembled).hexdigest()
            session.completed_at = time.time()
            return True, "UPLOAD_FULLY_ASSEMBLED", session

        return False, f"CHUNK_{chunk_index}_RECEIVED", session
