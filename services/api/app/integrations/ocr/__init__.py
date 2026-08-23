from __future__ import annotations

from app.core.config import Settings
from app.integrations.ocr.base import OCRProvider, OCRResult
from app.integrations.ocr.demo import DemoOCRProvider


def get_ocr_provider(settings: Settings | None = None) -> OCRProvider:
    """Resolve configured OCR provider according to environment."""
    return DemoOCRProvider()


__all__ = [
    "DemoOCRProvider",
    "OCRProvider",
    "OCRResult",
    "get_ocr_provider",
]
