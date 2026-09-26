"""
render_heatmap_svg.py — draw data/contributions.json as the classic
53-week x 7-day calendar of rounded boxes, with a diagonal slide-down reveal
that plays once on load and freezes (no looping "glow").

Usage:
    python scripts/render_heatmap_svg.py [data/contributions.json] [contrib-heatmap.svg]
"""
import json
import sys
from pathlib import Path

PALETTE = [
    "#161b22",  # level 0: none
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0",  # level 5: neon top end
]

CELL = 11
GAP = 3
RADIUS = 2
LEFT_PAD = 30       # room for day-of-week labels
TOP_PAD = 20         # room for month labels
LEGEND_H = 28
FOOTER_H = 26

REVEAL_DUR = 0.35
COL_STAGGER = 0.03   # each week-column starts slightly after the previous
ROW_STAGGER = 0.015  # plus a touch more per row, for the diagonal feel

MONTH_ABBR = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]
WEEKDAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}  # sparse, like GitHub's own


def load_data(path: str) -> dict:
    return json.loads(Path(path).read_text())


def weeks_from_days(days: list[dict]) -> list[list[dict]]:
    """Group flat day list into weeks (columns), Sunday-first, like GitHub."""
    from datetime import date as _date

    weeks: list[list[dict]] = []
    current_week: list[dict] = []

    for d in days:
        dow = _date.fromisoformat(d["date"]).weekday()  # Mon=0 .. Sun=6
        github_dow = (dow + 1) % 7  # convert to Sun=0 .. Sat=6

        if github_dow == 0 and current_week:
            weeks.append(current_week)
            current_week = []
        elif not current_week and github_dow != 0:
            # pad the first (partial) week so rows line up
            current_week = [None] * github_dow

        current_week.append(d)

    if current_week:
        while len(current_week) < 7:
            current_week.append(None)
        weeks.append(current_week)

    return weeks


def month_label_positions(weeks: list[list[dict]]) -> list[tuple[int, str]]:
    """Return (week_index, label) pairs where a new month starts."""
    from datetime import date as _date

    labels = []
    last_month = None
    for wi, week in enumerate(weeks):
        for day in week:
            if day is None:
                continue
            month = _date.fromisoformat(day["date"]).month
            if month != last_month:
                labels.append((wi, MONTH_ABBR[month - 1]))
                last_month = month
            break
    return labels


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(data: dict) -> str:
    weeks = weeks_from_days(data["days"])
    n_weeks = len(weeks)

    grid_w = n_weeks * (CELL + GAP)
    grid_h = 7 * (CELL + GAP)
    width = LEFT_PAD + grid_w + 20
    height = TOP_PAD + grid_h + LEGEND_H + FOOTER_H + 20

    cells_svg = []
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            if day is None:
                continue
            level = min(day.get("level", 0), len(PALETTE) - 1)
            color = PALETTE[level]
            x = LEFT_PAD + wi * (CELL + GAP)
            y = TOP_PAD + di * (CELL + GAP)
            begin = wi * COL_STAGGER + di * ROW_STAGGER

            cells_svg.append(f"""
    <rect x="{x}" y="{y - 6}" width="{CELL}" height="{CELL}" rx="{RADIUS}"
          fill="{color}" opacity="0">
      <title>{day['count']} contributions on {day['date']}</title>
      <animate attributeName="opacity" from="0" to="1"
               begin="{begin:.3f}s" dur="{REVEAL_DUR}s" fill="freeze" />
      <animate attributeName="y" from="{y - 6}" to="{y}"
               begin="{begin:.3f}s" dur="{REVEAL_DUR}s" fill="freeze"
               calcMode="spline" keySplines="0.2 0.8 0.2 1" />
    </rect>""")

    month_labels_svg = []
    for wi, label in month_label_positions(weeks):
        x = LEFT_PAD + wi * (CELL + GAP)
        month_labels_svg.append(
            f'<text x="{x}" y="{TOP_PAD - 8}" font-family="sans-serif" '
            f'font-size="11px" fill="#8b949e">{label}</text>'
        )

    weekday_labels_svg = []
    for dow, label in WEEKDAY_LABELS.items():
        y = TOP_PAD + dow * (CELL + GAP) + CELL
        weekday_labels_svg.append(
            f'<text x="0" y="{y}" font-family="sans-serif" font-size="10px" '
            f'fill="#8b949e">{label}</text>'
        )

    legend_y = TOP_PAD + grid_h + 22
    legend_svg = [
        f'<text x="{LEFT_PAD}" y="{legend_y}" font-family="sans-serif" '
        f'font-size="11px" fill="#8b949e">Less</text>'
    ]
    lx = LEFT_PAD + 34
    for color in PALETTE:
        legend_svg.append(
            f'<rect x="{lx}" y="{legend_y - 10}" width="{CELL}" height="{CELL}" '
            f'rx="{RADIUS}" fill="{color}" />'
        )
        lx += CELL + GAP
    legend_svg.append(
        f'<text x="{lx + 4}" y="{legend_y}" font-family="sans-serif" '
        f'font-size="11px" fill="#8b949e">More</text>'
    )

    footer_y = legend_y + FOOTER_H
    total = data.get("total_contributions", 0)
    current = data.get("current_streak", 0)
    longest = data.get("longest_streak", 0)
    footer_text = (
        f"{total:,} contributions in the last year &#8226; "
        f"current streak {current} &#8226; longest streak {longest}"
    )
    footer_svg = (
        f'<text x="{LEFT_PAD}" y="{footer_y}" font-family="sans-serif" '
        f'font-size="12px" fill="#8b949e">{footer_text}</text>'
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"
     width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="none"/>
{''.join(month_labels_svg)}
{''.join(weekday_labels_svg)}
{''.join(cells_svg)}
{''.join(legend_svg)}
{footer_svg}
</svg>"""


def main() -> None:
    data_path = sys.argv[1] if len(sys.argv) > 1 else "data/contributions.json"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "contrib-heatmap.svg"

    data = load_data(data_path)
    svg = build_svg(data)
    Path(out_path).write_text(svg)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()