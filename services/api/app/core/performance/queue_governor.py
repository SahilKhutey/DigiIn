"""
DigiIn Performance & Scalability — Multi-Queue Scaling Governor
Monitors queue depths across verification, document, and webhook pipelines and dynamically scales worker concurrency with backpressure protection.
"""

from __future__ import annotations


class QueueScalingGovernor:
    def __init__(
        self,
        base_concurrency: int = 5,
        max_concurrency: int = 50,
        high_watermark_depth: int = 500
    ):
        self.base_concurrency = base_concurrency
        self.max_concurrency = max_concurrency
        self.high_watermark_depth = high_watermark_depth
        self._queue_depths: dict[str, int] = {
            "verification": 0,
            "document": 0,
            "webhook": 0,
        }

    def update_queue_depth(self, queue_name: str, depth: int):
        self._queue_depths[queue_name] = depth

    def get_queue_depth(self, queue_name: str) -> int:
        return self._queue_depths.get(queue_name, 0)

    def calculate_worker_concurrency(self, queue_name: str) -> int:
        """Calculates optimal worker concurrency based on current backlog depth."""
        depth = self.get_queue_depth(queue_name)
        if depth == 0:
            return self.base_concurrency
        elif depth < 100:
            return self.base_concurrency
        elif depth < self.high_watermark_depth:
            # Scale proportionally
            scale_factor = depth / self.high_watermark_depth
            calculated = int(self.base_concurrency + (self.max_concurrency - self.base_concurrency) * scale_factor)
            return min(self.max_concurrency, calculated)
        else:
            return self.max_concurrency

    def is_backpressure_active(self, queue_name: str) -> bool:
        """Backpressure triggers if depth exceeds 2x high watermark."""
        return self.get_queue_depth(queue_name) > (self.high_watermark_depth * 2)
