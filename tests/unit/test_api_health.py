from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root_endpoint():
    """Verify root endpoint returns operational info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Multimodal Emotional Support Chatbot API" in data["message"]
    assert data["health"] == "/health"

def test_health_endpoint():
    """Verify /health endpoint returns valid system status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "database" in data
    assert data["database"]["connected"] is True
    assert "ai_provider" in data
    assert data["ai_provider"]["provider"] == "google-gemini"
