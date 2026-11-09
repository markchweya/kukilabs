"""Helpers shared by API tests."""

from fastapi.testclient import TestClient

from kuki.api import create_app
from kuki.llm import OllamaClient
from tests.fake_ollama import FakeOllama


def make_client(settings, fake: FakeOllama | None = None) -> tuple[TestClient, FakeOllama]:
    fake = fake or FakeOllama()
    llm = OllamaClient(settings.ollama_host, transport=fake.transport())
    llm._sleep = lambda _s: None
    return TestClient(create_app(settings, llm)), fake


NOTES = b"""# Uninformed search
BFS explores level by level using a FIFO queue. DFS goes deep first using a stack.

# Informed search
Heuristic: an estimate of the cost from a node to the goal.
A* expands the node with the lowest f(n) = g(n) + h(n).
"""


def upload_notes(client: TestClient, name: str = "week4.md", body: bytes = NOTES) -> dict:
    res = client.post("/api/documents", files={"file": (name, body, "text/markdown")})
    assert res.status_code == 201, res.text
    return res.json()
