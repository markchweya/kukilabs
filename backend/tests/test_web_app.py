from dataclasses import replace

from tests.api_helpers import make_client


def test_serves_spa_and_static_files(settings, tmp_path):
    web = tmp_path / "dist"
    (web / "assets").mkdir(parents=True)
    (web / "index.html").write_text("<div id=root></div>")
    (web / "assets" / "app.js").write_text("console.log(1)")
    (web / "kuki.svg").write_text("<svg/>")
    (tmp_path / "secret.txt").write_text("nope")

    client, _ = make_client(replace(settings, web_dir=web))
    assert client.get("/").text == "<div id=root></div>"
    assert client.get("/doc/abc/quiz").text == "<div id=root></div>"  # client-side route
    assert client.get("/assets/app.js").text == "console.log(1)"
    assert client.get("/kuki.svg").text == "<svg/>"
    assert "nope" not in client.get("/../secret.txt").text
    assert client.get("/api/nothing-here").status_code == 404
    assert client.get("/api/status").status_code == 200


def test_no_web_dir_means_api_only(settings):
    client, _ = make_client(replace(settings, web_dir=None))
    assert client.get("/").status_code == 404
