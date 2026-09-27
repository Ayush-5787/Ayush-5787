"""
make_ascii_svg.py — turn source-prepped.png into a self-typing ASCII portrait SVG.

Design choices (see the write-up for why):
  * Monochrome, one fill color -- per-character rainbow is what makes most
    ASCII art look like static.
  * High contrast source -- a busy background washes out to the space glyph
    so only the subject prints.
  * Each row wipes in left-to-right behind a clip-path, staggered top to
    bottom, with a small block "cursor" riding the wipe edge. The whole
    thing types once and freezes -- no looping.

Usage:
    python scripts/make_ascii_svg.py [source-prepped.png] [avi-ascii.svg]
"""
import sys
from pathlib import Path

from PIL import Image

# bright (sparse) -> dark (dense); leading space clears the background to nothing
RAMP = " .`:-=+*cs#%@"

COLS = 100
ROWS = 53

FONT_SIZE = 8
CHAR_W = FONT_SIZE * 0.6      # monospace advance width, roughly
LINE_H = FONT_SIZE * 1.05

FILL_COLOR = "#c9d1d9"        # single light-gray fill -- no rainbow
BG_COLOR = "none"             # transparent so it sits on the README's own bg

ROW_WIPE_DURATION = 0.55      # seconds for one row to fully wipe in
ROW_STAGGER = 0.05            # seconds between each row starting


def image_to_grid(img_path: str, cols: int = COLS, rows: int = ROWS) -> list[str]:
    """Downsample the prepped photo to a COLSxROWS character grid of glyphs."""
    img = Image.open(img_path).convert("L")
    small = img.resize((cols, rows), Image.LANCZOS)

    lines = []
    for y in range(rows):
        row_chars = []
        for x in range(cols):
            brightness = small.getpixel((x, y))  # 0 (black) - 255 (white)
            # invert + push midtones toward denser glyphs for a bolder, darker look
            darkness = ((255 - brightness) / 255) ** 0.6
            idx = int(darkness * (len(RAMP) - 1))
            row_chars.append(RAMP[idx])
        lines.append("".join(row_chars))
    return lines


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(rows: list[str]) -> str:
    width = COLS * CHAR_W + 20
    height = ROWS * LINE_H + 20

    body_parts = []
    for i, row_text in enumerate(rows):
        # skip fully-blank rows entirely (nothing to animate / no clip needed)
        if row_text.strip() == "":
            continue

        row_width = len(row_text) * CHAR_W
        y = 15 + i * LINE_H
        begin = round(i * ROW_STAGGER, 3)
        clip_id = f"wipe{i}"

        body_parts.append(f"""
  <clipPath id="{clip_id}">
    <rect x="0" y="{y - LINE_H}" width="0" height="{LINE_H + 4}">
      <animate attributeName="width" from="0" to="{row_width + CHAR_W}"
               begin="{begin}s" dur="{ROW_WIPE_DURATION}s"
               fill="freeze" calcMode="linear" />
    </rect>
  </clipPath>
  <g clip-path="url(#{clip_id})">
    <text x="10" y="{y}" font-family="monospace" font-size="{FONT_SIZE}px"
          fill="{FILL_COLOR}" xml:space="preserve">{escape_xml(row_text)}</text>
    <rect x="10" y="{y - FONT_SIZE}" width="{CHAR_W * 1.1}" height="{FONT_SIZE * 1.15}"
          fill="{FILL_COLOR}">
      <animate attributeName="x" from="10" to="{10 + row_width}"
               begin="{begin}s" dur="{ROW_WIPE_DURATION}s"
               fill="freeze" calcMode="linear" />
      <animate attributeName="opacity" from="1" to="0"
               begin="{begin + ROW_WIPE_DURATION}s" dur="0.15s" fill="freeze" />
    </rect>
  </g>""")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}"
     width="{width:.0f}" height="{height:.0f}">
  <rect width="100%" height="100%" fill="{BG_COLOR}"/>
{''.join(body_parts)}
</svg>"""


def main() -> None:
    src = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "avi-ascii.svg"

    if not Path(src).exists():
        raise FileNotFoundError(
            f"{src} not found -- run prep_photo.py on your source photo first."
        )

    grid = image_to_grid(src)
    svg = build_svg(grid)
    Path(out).write_text(svg)
    print(f"Wrote {out} ({len(grid)} rows x {COLS} cols)")


if __name__ == "__main__":
    main()