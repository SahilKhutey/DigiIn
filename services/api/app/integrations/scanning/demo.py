from __future__ import annotations

from typing import BinaryIO

from app.integrations.scanning.base import MalwareScanner, MalwareScanResult

# Standard EICAR test string signature snippet for testing malware rejection
EICAR_SIGNATURE = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"


class DemoMalwareScanner(MalwareScanner):
    """Simulated malware scanner for development and demo environments."""

    def scan(self, stream: BinaryIO) -> MalwareScanResult:
        stream.seek(0)
        content = stream.read(1024)
        stream.seek(0)

        if EICAR_SIGNATURE in content or b"MALWARE_TEST_SIGNATURE" in content:
            return MalwareScanResult(
                clean=False,
                provider="demo-clamav-guard",
                signature="Eicar-Test-Signature.Mock",
                simulated=True,
            )

        return MalwareScanResult(
            clean=True,
            provider="demo-clamav-guard",
            signature=None,
            simulated=True,
        )
