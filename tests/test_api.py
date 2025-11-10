from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_test_endpoint():
    resp = client.get("/test", params={"q": "abc"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "test ok"
    assert data["echo"] == "abc"


def test_ask_endpoint():
    payload = {"question": "Qual é a capital do Brasil?"}
    resp = client.post("/ask", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "Você perguntou" in data.get("answer", "")
