from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_ask_endpoint():
    payload = {"question": "O que é FastAPI?"}
    resp = client.post("/ask/gemma", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "FastAPI".upper() in data.get("answer", "").upper()
