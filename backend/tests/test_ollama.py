import httpx
import pytest
from pydantic import BaseModel

from kuki.llm import OllamaClient, OllamaError, OllamaUnavailable
from tests.fake_ollama import FakeOllama


class Answer(BaseModel):
    text: str
    score: int


def make(fake: FakeOllama) -> OllamaClient:
    client = OllamaClient("http://ollama.test", transport=fake.transport())
    client._sleep = lambda _s: None
    return client


def test_status_lists_models_and_matches_latest_tag():
    status = make(FakeOllama()).status()
    assert status.reachable
    assert status.has("llama3.2:3b")
    assert status.has("nomic-embed-text")  # bare name matches ":latest"
    assert not status.has("mistral")


def test_status_when_ollama_is_down():
    fake = FakeOllama()
    fake.down = True
    assert make(fake).status().reachable is False


def test_chat_json_parses_and_sends_schema():
    fake = FakeOllama()
    fake.respond("Answer", {"text": "hi", "score": 3})
    result = make(fake).chat_json("llama3.2:3b", [{"role": "user", "content": "q"}], Answer)
    assert result == Answer(text="hi", score=3)
    _, body = fake.requests[-1]
    assert body["format"]["title"] == "Answer"
    assert body["stream"] is False


def test_chat_json_repairs_invalid_output_once():
    fake = FakeOllama()
    replies = iter(['{"text": "hi", "score": "lots"}', '{"text": "hi", "score": 2}'])
    fake.respond("Answer", lambda _req: next(replies))
    result = make(fake).chat_json("m", [{"role": "user", "content": "q"}], Answer)
    assert result.score == 2
    # The retry shows the model its own bad answer and the error.
    _, retry = fake.requests[-1]
    assert "invalid" in retry["messages"][-1]["content"]


def test_chat_json_gives_up_after_attempts():
    fake = FakeOllama()
    fake.respond("Answer", '{"text": 1}')
    with pytest.raises(OllamaError, match="valid structured output"):
        make(fake).chat_json("m", [{"role": "user", "content": "q"}], Answer)


def test_unreachable_raises_unavailable():
    fake = FakeOllama()
    fake.down = True
    with pytest.raises(OllamaUnavailable):
        make(fake).chat("m", [{"role": "user", "content": "q"}])


def test_missing_model_is_reported():
    def handler(request):
        return httpx.Response(404, json={"error": "model 'x' not found"})

    client = OllamaClient("http://o", transport=httpx.MockTransport(handler))
    with pytest.raises(OllamaError, match="not found"):
        client.chat("x", [])


def test_busy_server_is_retried():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(503, json={"error": "busy"})
        return httpx.Response(200, json={"message": {"content": "ok"}})

    client = OllamaClient("http://o", transport=httpx.MockTransport(handler))
    client._sleep = lambda _s: None
    assert client.chat("m", []) == "ok"
    assert calls["n"] == 3


def test_embed_batches():
    fake = FakeOllama()
    vectors = make(fake).embed("nomic-embed-text", [f"t{i}" for i in range(5)], batch_size=2)
    assert len(vectors) == 5
    assert sum(1 for path, _ in fake.requests if path == "/api/embed") == 3
