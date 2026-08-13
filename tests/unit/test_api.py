from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def test_health_endpoint():
    from app.main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_root_endpoint():
    from app.main import app
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "RAG Platform" in data["message"]


def test_health_ready_all_ok():
    from app.main import app

    with patch("app.main._check_database", new_callable=AsyncMock, return_value="ok"), \
         patch("app.main._check_ollama", new_callable=AsyncMock, return_value="ok"), \
         patch("app.main._check_embedding", return_value="ok"):
        client = TestClient(app)
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["dependencies"]["postgres"] == "ok"
        assert data["dependencies"]["ollama"] == "ok"
        assert data["dependencies"]["embedding"] == "ok"


def test_health_ready_degraded():
    from app.main import app

    with patch("app.main._check_database", new_callable=AsyncMock, return_value="ok"), \
         patch("app.main._check_ollama", new_callable=AsyncMock, return_value="error"), \
         patch("app.main._check_embedding", return_value="ok"):
        client = TestClient(app)
        response = client.get("/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["dependencies"]["ollama"] == "error"


def test_health_ready_embedding_configured():
    from app.main import app

    with patch("app.main._check_database", new_callable=AsyncMock, return_value="ok"), \
         patch("app.main._check_ollama", new_callable=AsyncMock, return_value="ok"), \
         patch("app.main._check_embedding", return_value="configured"):
        client = TestClient(app)
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["dependencies"]["embedding"] == "configured"
