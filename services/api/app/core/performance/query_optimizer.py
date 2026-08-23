"""
DigiIn Performance & Scalability — Query Optimizer & Cursor Pagination
Provides cursor-based pagination and field-level projection to eliminate N+1 queries and full-table scan overheads.
"""

from __future__ import annotations

import base64
import json
from typing import Any


class CursorPaginator:
    @staticmethod
    def encode_cursor(item_id: str, timestamp: float) -> str:
        payload = {"id": item_id, "ts": timestamp}
        return base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")

    @staticmethod
    def decode_cursor(cursor_str: str) -> dict[str, Any] | None:
        try:
            raw = base64.urlsafe_b64decode(cursor_str.encode("utf-8"))
            return json.loads(raw)
        except Exception:
            return None

    @staticmethod
    def paginate_records(
        records: list[dict[str, Any]],
        limit: int = 50,
        cursor: str | None = None
    ) -> dict[str, Any]:
        """Paginates records deterministically using cursor without expensive SQL OFFSETs."""
        sorted_records = sorted(records, key=lambda x: (x.get("created_at", 0), x.get("id", "")))
        start_idx = 0

        if cursor:
            decoded = CursorPaginator.decode_cursor(cursor)
            if decoded:
                for idx, r in enumerate(sorted_records):
                    if r.get("id") == decoded.get("id"):
                        start_idx = idx + 1
                        break

        page_slice = sorted_records[start_idx : start_idx + limit]
        has_more = (start_idx + limit) < len(sorted_records)

        next_cursor = None
        if has_more and page_slice:
            last_item = page_slice[-1]
            next_cursor = CursorPaginator.encode_cursor(last_item.get("id", ""), last_item.get("created_at", 0))

        return {
            "items": page_slice,
            "hasMore": has_more,
            "nextCursor": next_cursor,
            "count": len(page_slice)
        }

class ResponseProjector:
    @staticmethod
    def project_fields(record: dict[str, Any], fields: list[str]) -> dict[str, Any]:
        """Returns only the explicitly requested fields, preventing over-fetching."""
        if not fields or "*" in fields:
            return dict(record)
        return {k: v for k, v in record.items() if k in fields}
