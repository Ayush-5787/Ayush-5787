import os

# EDIT THIS SECTION WITH YOUR DETAILS FROM GITHUB PROFILE
DATA = {
    "user": "Ayush-5787",
    "role": "AI & Full-Stack Developer",
    "edu": "B.Tech CSE · 3rd Year · PSIT Kanpur",
    "loc": "Kanpur, Uttar Pradesh, India",
    "stack": ["Python", "React", "Node.js", "LangChain"],
    "highlights": [
        "Building Multi-Agent Systems",
        "Open Source Contributor",
        "Ship > Perfect. Always."
    ]
}

COLOR_ACCENT = "#58a6ff" # Blue
COLOR_TEXT = "#c9d1d9"   # Gray
COLOR_DIM = "#8b949e"    # Dimmer Gray
BG_COLOR = "#0d1117"     # Dark BG

def generate_card(output_path="info-card.svg"):
    lines = []
    y_start = 20
    line_height = 25
    
    # Header
    lines.append(f'<text x="10" y="{y_start}" fill="{COLOR_ACCENT}" font-weight="bold" font-family="monospace" font-size="16px">ayush@github ~ $ neofetch</text>')
    y_current = y_start + line_height
    
    # Separator
    lines.append(f'<line x1="10" y1="{y_current}" x2="450" y2="{y_current}" stroke="{COLOR_DIM}" stroke-width="1" opacity="0.3"/>')
    y_current += line_height

    def add_kv(key, value, indent=0):
        nonlocal y_current
        k_x = 10 + indent
        v_x = 120 + indent
        lines.append(f'<text x="{k_x}" y="{y_current}" fill="{COLOR_DIM}" font-family="monospace" font-size="14px">{key}</text>')
        lines.append(f'<text x="{v_x}" y="{y_current}" fill="{COLOR_TEXT}" font-family="monospace" font-size="14px">{value}</text>')
        y_current += line_height

    add_kv("OS:", "Linux / Web")
    add_kv("User:", DATA["user"])
    add_kv("Role:", DATA["role"])
    add_kv("Edu:", DATA["edu"])
    add_kv("Loc:", DATA["loc"])
    
    y_current += 10 
    
    add_kv("Stack:", "")
    for item in DATA["stack"]:
        add_kv(f"  • {item}", "", indent=10)
        
    y_current += 10 
    
    add_kv("Focus:", "")
    for item in DATA["highlights"]:
        add_kv(f"  • {item}", "", indent=10)

    # Animation: Fade in lines sequentially
    animated_lines = []
    for i, line in enumerate(lines):
        delay = i * 0.1
        animated_lines.append(f'<g style="opacity:0; animation: fadeIn 0.5s ease-out {delay}s forwards;">{line}</g>')

    css = """
    <style>
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(5px); }
        to { opacity: 1; transform: translateY(0); }
      }
      text { dominant-baseline: middle; }
    </style>
    """

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 {y_current + 20}" width="480" height="{y_current + 20}">
{css}
<rect width="100%" height="100%" fill="{BG_COLOR}"/>
{''.join(animated_lines)}
</svg>'''

    with open(output_path, "w") as f:
        f.write(svg_content)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_card()