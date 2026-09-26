import json
import os
from datetime import datetime

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL_SIZE = 12
GAP = 3
COLS = 53
ROWS = 7

def render_svg(json_path="data/contributions.json", output_path="contrib-heatmap.svg"):
    days = []
    stats = {"total": 0}
    
    # Try to load real data
    if os.path.exists(json_path):
        try:
            with open(json_path) as f:
                data = json.load(f)
                days = data.get("days", [])
                stats = data.get("stats", {"total": 0})
        except Exception as e:
            print(f"Warning: Could not read JSON: {e}")

    # If no data found, create dummy zeros so grid renders
    if not days:
        for _ in range(COLS * ROWS):
            days.append({"level": 0})

    weeks = []
    current_week = []
    
    for day in days:
        current_week.append(day)
        if len(current_week) == ROWS:
            weeks.append(current_week)
            current_week = []
            
    if current_week:
        while len(current_week) < ROWS:
            current_week.append({"level": 0})
        weeks.append(current_week)

    # Ensure exactly COLS weeks
    while len(weeks) < COLS:
        weeks.insert(0, [{"level": 0}] * ROWS)
    weeks = weeks[-COLS:]

    width = COLS * (CELL_SIZE + GAP) + 40
    height = ROWS * (CELL_SIZE + GAP) + 60
    
    rects = []
    
    for col_idx, week in enumerate(weeks):
        for row_idx, day in enumerate(week):
            level = min(int(day.get("level", 0)), 4)
            color = PALETTE[level]
            x = 20 + col_idx * (CELL_SIZE + GAP)
            y = 20 + row_idx * (CELL_SIZE + GAP)
            
            rect_id = f"c_{col_idx}_{row_idx}"
            rects.append(f'<rect id="{rect_id}" x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" rx="2" ry="2" fill="{color}" opacity="0" />')
            
    css_rules = []
    for col_idx, week in enumerate(weeks):
        for row_idx, day in enumerate(week):
             delay = (col_idx + row_idx) * 0.02
             sel = f"#c_{col_idx}_{row_idx}"
             css_rules.append(f'{sel} {{ animation: reveal 0.5s ease-out {delay}s forwards; }}')

    css_block = "<style>" + "".join(css_rules) + """
    @keyframes reveal {
      from { opacity: 0; transform: scale(0.5); }
      to { opacity: 1; transform: scale(1); }
    }
    text { font-family: sans-serif; fill: #8b949e; font-size: 12px; }
    </style>"""

    header_text = f"{stats['total']} contributions in the last year"
    
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
{css_block}
<text x="20" y="15" fill="#c9d1d9" font-weight="bold">{header_text}</text>
{''.join(rects)}
<text x="20" y="{height - 10}">Less</text>
<rect x="55" y="{height - 20}" width="10" height="10" fill="{PALETTE[0]}" rx="2"/>
<rect x="68" y="{height - 20}" width="10" height="10" fill="{PALETTE[1]}" rx="2"/>
<rect x="81" y="{height - 20}" width="10" height="10" fill="{PALETTE[2]}" rx="2"/>
<rect x="94" y="{height - 20}" width="10" height="10" fill="{PALETTE[3]}" rx="2"/>
<rect x="107" y="{height - 20}" width="10" height="10" fill="{PALETTE[4]}" rx="2"/>
<text x="125" y="{height - 10}">More</text>
</svg>'''

    with open(output_path, "w") as f:
        f.write(svg_content)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    render_svg()