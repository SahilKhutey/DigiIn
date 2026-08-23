from io import BytesIO

import pytest

from app.integrations.storage.local import LocalObjectStorage


def test_local_storage_hashes_stream(tmp_path):
    storage = LocalObjectStorage(str(tmp_path))
    result = storage.put(BytesIO(b"digiin-document"), content_type="application/pdf")

    assert result.size_bytes == 15
    assert len(result.content_hash) == 64
    assert storage.open(result.object_id).read() == b"digiin-document"


def test_local_storage_rejects_wrong_expected_hash(tmp_path):
    storage = LocalObjectStorage(str(tmp_path))

    with pytest.raises(ValueError, match="hash mismatch"):
        storage.put(
            BytesIO(b"digiin-document"),
            content_type="application/pdf",
            expected_hash="0" * 64,
        )
