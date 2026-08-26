from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_document_routes_exist():
    paths={r.path for r in app.routes}
    assert '/api/v1/documents/upload' in paths
    assert '/api/v1/review/documents' in paths
    assert '/api/v1/review/documents/{document_id}/decision' in paths
