"""
make_info_card.py — neofetch-style panel that "prints" next to the portrait.

Edit DATA below with your own details. Keep story-telling content here
(role, what you're doing now/before, highlights) rather than duplicating
GitHub stats -- the heatmap already covers those.

STATIC=1 emits a frozen final frame (handy for a local Quick Look preview
that doesn't play SMIL).

Usage:
    python scripts/make_info_card.py [info-card.svg]
    STATIC=1 python scripts/make_info_card.py preview.svg
"""
import os
import sys
from pathlib import Path

DATA = {
    "name": "Ayush Nandan",
    "role": "AI & Full-Stack Developer",
    "now": "Building multi-agent LLM systems",
    "prev": "Full-stack web apps (React / Node.js)",
    "stack": ["Python", "React", "Node.js", "LangChain", "Git"],
    "highlights": [
        "B.Tech CSE, PSIT Kanpur",
        "Kanpur, India",
    ],
}

WIDTH = 490
FONT = "SFMono-Regular, Consolas, monospace"
BG = "#0d1117"
BORDER = "#30363d"
LABEL_COLOR = "#8b949e"
VALUE_COLOR = "#c9d1d9"
ACCENT = "#58a6ff"
TITLEBAR_H = 34
PAD_X = 20
LINE_H = 24

FADE_DUR = 0.35
LINE_STAGGER = 0.12
START_DELAY = 0.3  # let the title bar draw first


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def kv_lines():
    """(label, value) rows in display order."""
    rows = [
        ("os", "human@kanpur"),
        ("role", DATA["role"]),
        ("now", DATA["now"]),
        ("prev", DATA["prev"]),
        ("stack", ", ".join(DATA["stack"])),
    ]
    labels = ["edu", "loc"]
    for label, h in zip(labels, DATA["highlights"]):
        rows.append((label, h))
    return rows


def build_svg(static: bool) -> str:
    rows = kv_lines()
    body_y = TITLEBAR_H + 34
    height = body_y + len(rows) * LINE_H + 20

    lines_svg = []
    for i, (label, value) in enumerate(rows):
        y = body_y + i * LINE_H
        begin = START_DELAY + i * LINE_STAGGER

        if static:
            transform = ""
            opacity_attrs = ""
        else:
            transform = 'transform="translate(-14,0)"'
            opacity_attrs = "opacity=\"0\""

        anims = "" if static else f"""
      <animate attributeName="opacity" from="0" to="1"
               begin="{begin:.2f}s" dur="{FADE_DUR}s" fill="freeze" />
      <animateTransform attributeName="transform" type="translate"
               from="-14 0" to="0 0"
               begin="{begin:.2f}s" dur="{FADE_DUR}s" fill="freeze" />"""

        lines_svg.append(f"""
    <g {opacity_attrs} {transform}>
      <text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="13px"
            fill="{LABEL_COLOR}">{esc(label)}</text>
      <text x="{PAD_X + 65}" y="{y}" font-family="{FONT}" font-size="13px"
            fill="{VALUE_COLOR}">{esc(value)}</text>
      {anims}
    </g>""")

    name_opacity = "1" if static else "0"
    name_anim = "" if static else f"""
      <animate attributeName="opacity" from="0" to="1" begin="0s" dur="0.3s" fill="freeze" />"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}"
     width="{WIDTH}" height="{height}">
  <rect width="100%" height="100%" rx="8" fill="{BG}" stroke="{BORDER}" />

  <rect width="100%" height="{TITLEBAR_H}" rx="8" fill="{BG}" />
  <rect y="{TITLEBAR_H - 1}" width="100%" height="1" fill="{BORDER}" />
  <circle cx="20" cy="{TITLEBAR_H / 2}" r="5" fill="#ff5f56" />
  <circle cx="38" cy="{TITLEBAR_H / 2}" r="5" fill="#ffbd2e" />
  <circle cx="56" cy="{TITLEBAR_H / 2}" r="5" fill="#27c93f" />
  <text x="{WIDTH / 2}" y="{TITLEBAR_H / 2 + 4}" text-anchor="middle"
        font-family="{FONT}" font-size="12px" fill="{LABEL_COLOR}">neofetch</text>

  <text x="{PAD_X}" y="{TITLEBAR_H + 20}" font-family="{FONT}" font-size="15px"
        font-weight="bold" fill="{ACCENT}" opacity="{name_opacity}">{esc(DATA["name"])}{name_anim}</text>

{''.join(lines_svg)}
</svg>"""


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else "info-card.svg"
    static = os.environ.get("STATIC") == "1"
    svg = build_svg(static)
    Path(out).write_text(svg)
    print(f"Wrote {out}{' (static preview)' if static else ''}")


if __name__ == "__main__":
    main()