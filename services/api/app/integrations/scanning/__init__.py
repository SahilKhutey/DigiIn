from __future__ import annotations

from app.core.config import Settings
from app.integrations.scanning.base import MalwareScanner, MalwareScanResult
from app.integrations.scanning.demo import DemoMalwareScanner


def get_malware_scanner(settings: Settings | None = None) -> MalwareScanner:
    """Resolve configured malware scanner according to environment."""
    return DemoMalwareScanner()


__all__ = [
    "DemoMalwareScanner",
    "MalwareScanResult",
    "MalwareScanner",
    "get_malware_scanner",
]
