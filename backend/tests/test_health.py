from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_me_requires_auth():
    response = client.get("/me")
    # No Authorization header -> FastAPI's HTTPBearer rejects with 403
    assert response.status_code in (401, 403)
