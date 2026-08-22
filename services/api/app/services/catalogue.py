"""Intent-first document catalogue for the prototype."""

from app.domain.models import DocumentOption

DOCUMENTS = [
    DocumentOption(id="marksheet", label="Class XII marksheet", category="Education", trustLabel="Government issued"),
    DocumentOption(id="driving-licence", label="Driving licence", category="Transport", trustLabel="Government issued"),
    DocumentOption(id="uploaded-file", label="My uploaded file", category="Personal upload", trustLabel="User uploaded"),
]


def search_documents(query: str = "") -> list[DocumentOption]:
    normalized = query.strip().casefold()
    if not normalized:
        return DOCUMENTS
    return [item for item in DOCUMENTS if normalized in f"{item.label} {item.category}".casefold()]


def get_document(document_id: str) -> DocumentOption | None:
    return next((item for item in DOCUMENTS if item.id == document_id), None)
