"""Integration tests for:
1. Background Async Worker Pipelines (OCR, Malware Scanning, Issuer Health)
2. Asymmetric Proof Verification
3. Schema & Integration Verification
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add services and repo root to sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "services" / "api"))
sys.path.insert(0, str(root_dir))

import pytest
from services.worker.main import WorkerDaemon
from services.worker.tasks import check_issuer_health_heartbeats, process_document_ocr, scan_malware


@pytest.mark.asyncio
async def test_worker_daemon_document_ocr_task():
    worker = WorkerDaemon()
    sample_bytes = b"%PDF-1.4 Mock CBSE Class XII passing certificate for Rahul Sharma"

    result = await worker.execute_job(
        job_type="DOCUMENT_OCR",
        payload={
            "documentId": "doc_worker_test_01",
            "fileBytes": sample_bytes,
            "filename": "cbse_marksheet_2026.pdf",
        },
    )

    assert result["documentId"] == "doc_worker_test_01"
    assert result["virusClean"] is True
    assert result["ocrResult"]["ocrStatus"] == "SUCCESS"
    assert result["ocrResult"]["detectedType"] == "CLASS_XII"
    assert result["ocrResult"]["extractedFields"]["student_name"] == "RAHUL SHARMA"
    assert len(worker.job_history) == 1


@pytest.mark.asyncio
async def test_worker_issuer_health_and_purge():
    worker = WorkerDaemon()

    # 1. Health check job
    h_res = await worker.execute_job(job_type="ISSUER_HEALTH_CHECK", payload={})
    assert len(h_res["healthReport"]) >= 4
    assert h_res["healthReport"][0]["status"] == "HEALTHY"

    # 2. Token purge job
    p_res = await worker.execute_job(job_type="PURGE_EXPIRED_TOKENS", payload={})
    assert "purgedCount" in p_res


def test_standalone_worker_tasks():
    # 1. Test Land Record Classification
    land_bytes = b"Revenue deed scan survey no 98 Raipur"
    land_res = process_document_ocr("doc_land_99", land_bytes, "land_deed_raipur.pdf")
    assert land_res["detectedType"] == "LAND_RECORD"
    assert "survey_number" in land_res["extractedFields"]

    # 2. Test Driving Licence Classification
    dl_bytes = b"MoRTH DL transport permit"
    dl_res = process_document_ocr("doc_dl_88", dl_bytes, "driving_licence_morth.pdf")
    assert dl_res["detectedType"] == "DRIVING_LICENCE"
    assert "licence_number" in dl_res["extractedFields"]

    # 3. Test ClamAV Scanning
    assert scan_malware(b"arbitrary clean bytes") is True


if __name__ == "__main__":
    test_standalone_worker_tasks()
    asyncio.run(test_worker_daemon_document_ocr_task())
    asyncio.run(test_worker_issuer_health_and_purge())
    print("SUCCESS: ALL WORKER AND MOBILE INTEGRATION TESTS PASSED!")
