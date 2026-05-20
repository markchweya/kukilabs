from __future__ import annotations

from io import BytesIO

from PIL import Image, ImageDraw


LOGO_SVG = """
<svg viewBox="0 0 40 40" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="kuki-dot-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1" stdDeviation="1.1" flood-color="#0F172A" flood-opacity=".13"/>
    </filter>
  </defs>
  <g filter="url(#kuki-dot-shadow)">
    <circle cx="20" cy="21" r="6.1" fill="#111111"/>
    <circle cx="20" cy="8.6" r="4.3" fill="#111111"/>
    <circle cx="30.7" cy="26.8" r="4.3" fill="#2563EB"/>
    <circle cx="9.3" cy="26.8" r="4.3" fill="#14B8A6"/>
  </g>
  <path d="M20 14.2v-2.1M25.2 24.2l2 1.1M14.8 24.2l-2 1.1" fill="none" stroke="#111111" stroke-width="1.8" stroke-linecap="round" opacity=".26"/>
</svg>
""".strip()


def get_logo_svg() -> str:
    return LOGO_SVG


def get_page_icon() -> Image.Image:
    image = Image.new("RGBA", (128, 128), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    scale = 128 / 40

    def circle(cx: float, cy: float, radius: float, color: tuple[int, int, int, int]) -> None:
        x = cx * scale
        y = cy * scale
        r = radius * scale
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)

    circle(20, 21, 6.1, (17, 17, 17, 255))
    circle(20, 8.6, 4.3, (17, 17, 17, 255))
    circle(30.7, 26.8, 4.3, (37, 99, 235, 255))
    circle(9.3, 26.8, 4.3, (20, 184, 166, 255))

    # Small connector hints matching the SVG mark.
    line_color = (17, 17, 17, 66)
    width = max(2, round(1.8 * scale))
    draw.line(((20 * scale, 14.2 * scale), (20 * scale, 12.1 * scale)), fill=line_color, width=width)
    draw.line(((25.2 * scale, 24.2 * scale), (27.2 * scale, 25.3 * scale)), fill=line_color, width=width)
    draw.line(((14.8 * scale, 24.2 * scale), (12.8 * scale, 25.3 * scale)), fill=line_color, width=width)

    return image


def get_page_icon_bytes() -> bytes:
    buffer = BytesIO()
    get_page_icon().save(buffer, format="PNG")
    return buffer.getvalue()
