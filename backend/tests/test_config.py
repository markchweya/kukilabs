from pathlib import Path

from kuki.config import load_settings


def test_defaults(monkeypatch):
    for var in ("OLLAMA_HOST", "KUKI_MODEL", "KUKI_NUM_CTX", "KUKI_DATA_DIR"):
        monkeypatch.delenv(var, raising=False)
    s = load_settings()
    assert s.ollama_host == "http://localhost:11434"
    assert s.chat_model == "llama3.2:3b"
    assert s.data_dir == Path.home() / ".kuki"


def test_env_overrides(monkeypatch, tmp_path):
    monkeypatch.setenv("OLLAMA_HOST", "http://box:11434/")
    monkeypatch.setenv("KUKI_MODEL", "qwen2.5:7b")
    monkeypatch.setenv("KUKI_DATA_DIR", str(tmp_path))
    s = load_settings()
    assert s.ollama_host == "http://box:11434"  # trailing slash stripped
    assert s.chat_model == "qwen2.5:7b"
    assert s.db_path == tmp_path / "kuki.db"


def test_bad_numbers_fall_back(monkeypatch):
    monkeypatch.setenv("KUKI_NUM_CTX", "lots")
    assert load_settings().num_ctx == 8192
    monkeypatch.setenv("KUKI_NUM_CTX", "100")
    assert load_settings().num_ctx == 2048  # clamped to the minimum


def test_bool_parsing(monkeypatch):
    monkeypatch.setenv("KUKI_ALLOW_DOWNLOADS", "no")
    assert load_settings().allow_downloads is False
    monkeypatch.setenv("KUKI_ALLOW_DOWNLOADS", "YES")
    assert load_settings().allow_downloads is True
