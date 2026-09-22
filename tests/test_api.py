from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "tickets_loaded" in data

def test_get_anomalies():
    response = client.get("/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_query_empty():
    response = client.post("/query", json={"question": "   "})
    assert response.status_code == 400
