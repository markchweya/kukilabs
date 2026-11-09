from fastapi.testclient import TestClient

from kuki.api import create_app
from kuki.llm import OllamaClient
from tests.fake_ollama import FakeOllama


def client_for(settings, fake):
    return TestClient(create_app(settings, OllamaClient(settings.ollama_host, transport=fake.transport())))


def test_status_ready(settings):
    body = client_for(settings, FakeOllama()).get("/api/status").json()
    assert body["ai_ready"] is True
    assert body["checks"]["ollama"]["ok"] is True
    assert body["checks"]["embed_model"]["fix"] is None


def test_status_explains_how_to_fix(settings):
    fake = FakeOllama(models=[])
    body = client_for(settings, fake).get("/api/status").json()
    assert body["ai_ready"] is False
    assert body["checks"]["chat_model"]["fix"] == "ollama pull llama3.2:3b"
    fake.down = True
    body = client_for(settings, fake).get("/api/status").json()
    assert "ollama serve" in body["checks"]["ollama"]["fix"]
