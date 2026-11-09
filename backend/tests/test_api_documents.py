from dataclasses import replace

from tests.api_helpers import make_client, upload_notes


def test_upload_processes_in_background_and_lists(settings):
    client, fake = make_client(settings)
    created = upload_notes(client)
    assert created["status"] == "processing" and created["title"] == "week4"

    # TestClient runs background tasks before returning, so it is ready now.
    doc = client.get(f"/api/documents/{created['id']}").json()
    assert doc["status"] == "ready" and doc["segment_count"] == 2
    assert [d["id"] for d in client.get("/api/documents").json()] == [created["id"]]
    segments = client.get(f"/api/documents/{created['id']}/segments").json()
    assert segments[0]["locator"] == "Section: Uninformed search"
    assert any(path == "/api/embed" for path, _ in fake.requests)


def test_unsupported_type_rejected_before_saving(settings):
    client, _ = make_client(settings)
    res = client.post("/api/documents", files={"file": ("x.exe", b"MZ", "application/octet-stream")})
    assert res.status_code == 422 and "can't read" in res.json()["detail"]
    assert client.get("/api/documents").json() == []


def test_oversized_upload_rejected_and_cleaned_up(settings):
    client, _ = make_client(replace(settings, max_upload_mb=1))
    res = client.post("/api/documents", files={"file": ("big.txt", b"x" * (2 * 1024 * 1024), "text/plain")})
    assert res.status_code == 413
    assert client.get("/api/documents").json() == []
    assert list(settings.uploads_dir.iterdir()) == []


def test_unreadable_file_marked_failed(settings):
    client, _ = make_client(settings)
    doc = upload_notes(client, "empty.txt", b"   ")
    got = client.get(f"/api/documents/{doc['id']}").json()
    assert got["status"] == "failed" and "No readable text" in got["error"]


def test_path_traversal_filenames_are_flattened(settings):
    client, _ = make_client(settings)
    doc = upload_notes(client, "../../etc/notes.md")
    assert doc["filename"] == "notes.md"


def test_delete_and_404(settings):
    client, _ = make_client(settings)
    doc = upload_notes(client)
    assert client.delete(f"/api/documents/{doc['id']}").status_code == 204
    assert client.get(f"/api/documents/{doc['id']}").status_code == 404
