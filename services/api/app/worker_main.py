"""DigiIn Standalone Background Worker Process."""

from __future__ import annotations

import time

from app.core.operations.job_worker import job_worker
from app.db.session import init_db


def run_worker_loop():
    init_db()
    print("DigiIn Background Job Worker active. Polling queues...")
    while True:
        try:
            job_worker.process_all()
        except Exception as exc:
            print(f"Worker iteration error: {exc}")
        time.sleep(1)

if __name__ == "__main__":
    run_worker_loop()
