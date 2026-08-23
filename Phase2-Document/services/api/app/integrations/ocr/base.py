from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO, Protocol


@dataclass(frozen=True)
class OCRResult:
    text: str
    language: str | None
    confidence: float
    provider: str
    simulated: bool = False


class OCRProvider(Protocol):
    def extract(self, stream: BinaryIO, *, content_type: str) -> OCRResult:
        ...
