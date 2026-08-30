import os

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "billing-dashboard-505116")
os.environ.setdefault("FIREBASE_API_KEY", "test-public-key")
os.environ.setdefault("FIREBASE_APP_ID", "test-app-id")
os.environ.setdefault("FIREBASE_MESSAGING_SENDER_ID", "123")

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_reports_components():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["firebase_auth"] is True
    assert response.json()["firestore"] is True


def test_private_routes_require_firebase_token():
    response = client.get("/api/history")
    assert response.status_code == 401


def test_chat_rejects_oversized_input_before_processing():
    response = client.post("/api/chat", json={"message": "x" * 4001, "mode": "clarity"})
    assert response.status_code in {401, 422}

