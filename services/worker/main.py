"""Worker daemon runner."""

from __future__ import annotations

import logging
from services.worker.tasks import process_document_ocr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")


def start_worker() -> None:
    logger.info("DigiLocker X Background Worker service initialized.")


if __name__ == "__main__":
    start_worker()
