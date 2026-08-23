from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO, Protocol


@dataclass(frozen=True)
class StoredObject:
    object_id: str
    content_hash: str
    size_bytes: int
    content_type: str


class ObjectStorage(Protocol):
    """Provider boundary for document/object persistence."""

    def put(
        self,
        stream: BinaryIO,
        *,
        content_type: str,
        expected_hash: str | None = None,
    ) -> StoredObject:
        ...

    def open(self, object_id: str) -> BinaryIO:
        ...

    def delete(self, object_id: str) -> None:
        ...
