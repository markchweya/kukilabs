"""Turn an HTML page into Markdown-ish text using only the standard library.

Headings become "## Heading" lines so the existing Markdown segmenter can split
the page into sections, which then become citation locators.
"""

from __future__ import annotations

from html.parser import HTMLParser

# Paragraph-like blocks get a blank line around them; line-like blocks one newline.
_PARAGRAPH = {"p", "pre", "blockquote", "section", "article", "table", "ul", "ol"}
_LINE = {"div", "li", "tr", "br"}
_HEADING = {"h1": "#", "h2": "##", "h3": "###", "h4": "####"}
_SKIP = {"script", "style", "nav", "footer", "header", "noscript", "svg", "form", "button"}


class _Extractor(HTMLParser):
    def __init__(self, root_id: str | None, root_tag: str | None):
        super().__init__(convert_charrefs=True)
        self.root_id, self.root_tag = root_id, root_tag
        self.inside = root_id is None and root_tag is None
        self.depth = 0          # nesting depth within the root element
        self.skip = 0           # >0 while inside script/style/nav...
        self.out: list[str] = []
        self.pending = 0        # newlines owed before the next text
        self.prefix = ""        # e.g. "## " for the next heading text

    def _break(self, newlines: int) -> None:
        # Adjacent block boundaries ask for the *larger* break, not the sum,
        # so </li><li> stays a single newline.
        self.pending = max(self.pending, newlines)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if not self.inside:
            if (self.root_id and attrs.get("id") == self.root_id) or (self.root_tag and tag == self.root_tag):
                self.inside, self.depth = True, 1
            return
        if tag not in ("br", "img", "hr", "input", "meta", "link"):
            self.depth += 1
        if tag in _SKIP:
            self.skip += 1
        elif tag in _HEADING:
            self._break(2)
            self.prefix = _HEADING[tag] + " "
        elif tag in _PARAGRAPH:
            self._break(2)
        elif tag in _LINE:
            self._break(1)
        elif tag == "code":
            self.handle_data("`")

    def handle_endtag(self, tag):
        if not self.inside:
            return
        if tag in _SKIP and self.skip:
            self.skip -= 1
        elif tag in _HEADING or tag in _PARAGRAPH:
            self._break(2)
        elif tag in _LINE:
            self._break(1)
        elif tag == "code":
            self.handle_data("`")
        self.depth -= 1
        if self.depth <= 0 and (self.root_id or self.root_tag):
            self.inside = False

    def handle_data(self, data):
        if not self.inside or self.skip:
            return
        if not data.strip():
            if not self.pending:
                self.out.append(" ")
            return
        if self.pending and self.out:
            self.out.append("\n" * self.pending)
        self.pending = 0
        self.out.append(self.prefix + data)
        self.prefix = ""


def html_to_text(html: str, *, root_id: str | None = None, root_tag: str | None = None) -> str:
    """Extract readable text, optionally only inside the element with `root_id` or first `root_tag`."""
    parser = _Extractor(root_id, root_tag)
    parser.feed(html)
    parser.close()
    lines = [" ".join(line.split()) for line in "".join(parser.out).split("\n")]
    return "\n".join(lines).strip()
