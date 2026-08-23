from __future__ import annotations

from typing import BinaryIO

from app.integrations.ocr.base import OCRProvider, OCRResult


class DemoOCRProvider(OCRProvider):
    """Simulated OCR extraction provider for development and testing."""

    def extract(self, stream: BinaryIO, *, content_type: str) -> OCRResult:
        stream.seek(0)
        raw_bytes = stream.read(4096)
        stream.seek(0)

        # Attempt utf-8 decoding or synthesize structured mock text
        try:
            decoded = raw_bytes.decode("utf-8", errors="ignore").strip()
        except Exception:
            decoded = ""

        if not decoded:
            decoded = "CENTRAL BOARD OF SECONDARY EDUCATION\nMARKS STATEMENT\nNAME: SAHIL KHUTEY\nROLL: 2026-99214\nYEAR: 2026\nRESULT: PASS (94.2%)"

        return OCRResult(
            text=decoded,
            language="en",
            confidence=0.95,
            provider="demo-tesseract-engine",
            simulated=True,
        )
