from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO, Protocol


@dataclass(frozen=True)
class MalwareScanResult:
    clean: bool
    provider: str
    signature: str | None = None
    simulated: bool = False


class MalwareScanner(Protocol):
    def scan(self, stream: BinaryIO) -> MalwareScanResult:
        ...
