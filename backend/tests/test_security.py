from dataclasses import replace

from tests.api_helpers import make_client


def test_rejects_foreign_host_headers(settings):
    client, _ = make_client(settings)
    assert client.get("/api/status", headers={"host": "localhost:8765"}).status_code == 200
    assert client.get("/api/status", headers={"host": "127.0.0.1:8765"}).status_code == 200
    # A rebinding attacker's domain resolving to 127.0.0.1 is refused.
    assert client.get("/api/status", headers={"host": "evil.example"}).status_code == 400


def test_extra_hosts_can_be_allowed(settings):
    client, _ = make_client(replace(settings, extra_hosts=("study-pc.local",)))
    assert client.get("/api/status", headers={"host": "study-pc.local"}).status_code == 200


def test_cors_allows_local_dev_origin_only(settings):
    client, _ = make_client(settings)
    ok = client.get("/api/status", headers={"origin": "http://localhost:5173"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    bad = client.get("/api/status", headers={"origin": "https://evil.example"})
    assert "access-control-allow-origin" not in bad.headers
