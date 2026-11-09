from kuki.openlib.html_text import html_to_text

PAGE = """
<html><head><style>.x{}</style><script>alert(1)</script></head><body>
<nav>Menu Home About</nav>
<main>
  <h1>Lecture 0</h1>
  <h2>Search</h2>
  <p>A <b>search problem</b> has an initial state.</p>
  <ul><li>Actions</li><li>Transition model</li></ul>
  <h2>Frontier</h2><p>Use <code>queue</code> for BFS.</p>
</main>
<footer>Copyright</footer>
</body></html>
"""


def test_extracts_main_with_markdown_headings():
    text = html_to_text(PAGE, root_tag="main")
    assert text.startswith("# Lecture 0")
    assert "## Search\n\nA search problem has an initial state." in text
    assert "Actions\nTransition model" in text
    assert "Use `queue` for BFS." in text
    assert "Menu" not in text and "alert" not in text and "Copyright" not in text


def test_root_id_and_nesting():
    html = '<div id="a"><div><p>inner</p></div><p>still in</p></div><p>outside</p>'
    assert html_to_text(html, root_id="a") == "inner\n\nstill in"
