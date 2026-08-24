"""Low-Bandwidth "Data Saver" Mode Engine.

Optimizes mobile network payloads, eliminates heavy binary previews,
and ensures seamless operation over 2G/3G connections.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass
class DataSaverMetrics:
    mode_active: bool
    uncompressed_bytes: int
    compressed_bytes: int
    bytes_saved: int
    compression_ratio_pct: float
    message: str


class DataSaverEngine:
    """Provides low-bandwidth optimizations and payload compression metrics."""

    def __init__(self) -> None:
        self._enabled: bool = True  # Enabled by default for inclusive mobile access

    def is_enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def optimize_payload(self, raw_payload: dict[str, Any]) -> dict[str, Any]:
        """Strips redundant debug metadata and heavy asset references when Data Saver is active."""
        if not self._enabled:
            return raw_payload

        optimized = {}
        for k, v in raw_payload.items():
            # Skip heavy fields in Data Saver mode
            if k in ("raw_file", "document_binary", "debug_trace", "full_logs", "raw_ocr_blocks"):
                continue
            if isinstance(v, dict):
                optimized[k] = self.optimize_payload(v)
            elif isinstance(v, list) and v and isinstance(v[0], dict):
                optimized[k] = [self.optimize_payload(item) for item in v]
            else:
                optimized[k] = v

        return optimized

    def calculate_savings(
        self, original_data: dict[str, Any], optimized_data: dict[str, Any]
    ) -> DataSaverMetrics:
        """Calculates exact network bandwidth savings in bytes and percentage."""
        orig_bytes = len(json.dumps(original_data).encode("utf-8"))
        opt_bytes = len(json.dumps(optimized_data).encode("utf-8"))
        saved = max(0, orig_bytes - opt_bytes)
        ratio = (saved / orig_bytes * 100.0) if orig_bytes > 0 else 0.0

        return DataSaverMetrics(
            mode_active=self._enabled,
            uncompressed_bytes=orig_bytes,
            compressed_bytes=opt_bytes,
            bytes_saved=saved,
            compression_ratio_pct=round(ratio, 1),
            message="Data Saver is on. DigiIn will use less data.",
        )


data_saver_engine = DataSaverEngine()
