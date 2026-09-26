import os

DATA = {
    "name": "Ayush Nandan",
    "role": "AI & Full-Stack Developer",
    "edu": "B.Tech CSE · PSIT Kanpur",
    "loc": "Kanpur, India",
    "skills": ["Python", "React", "Node.js", "LangChain"],
    "focus": ["Multi-Agent Systems", "Open Source", "Ship > Perfect"]
}

COLOR_ACCENT = "#58a6ff" 
COLOR_TEXT = "#c9d1d9"   
COLOR_DIM = "#8b949e"    
BG_COLOR = "#0d1117"     

def escape_xml(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def generate_card(output_path="info-card.svg"):
    lines = []
    y = 30
    lh = 28
    
    # Title
    lines.append(f'<text x="20" y="{y}" fill="{COLOR_ACCENT}" font-weight="bold" font-family="sans-serif" font-size="20px">{escape_xml(DATA["name"])}</text>')
    y += lh
    
    # Role
    lines.append(f'<text x="20" y="{y}" fill="{COLOR_TEXT}" font-family="sans-serif" font-size="16px">{escape_xml(DATA["role"])}</text>')
    y += lh + 10
    
    # Divider
    lines.append(f'<line x1="20" y1="{y}" x2="460" y2="{y}" stroke="{COLOR_DIM}" stroke-width="1" opacity="0.3"/>')
    y += lh

    def add_item(label, value):
        nonlocal y
        lines.append(f'<text x="20" y="{y}" fill="{COLOR_DIM}" font-family="sans-serif" font-size="14px">{escape_xml(label)}</text>')
        lines.append(f'<text x="100" y="{y}" fill="{COLOR_TEXT}" font-family="sans-serif" font-size="14px">{escape_xml(value)}</text>')
        y += lh

    add_item("Education:", DATA["edu"])
    add_item("Location:", DATA["loc"])
    
    y += 10
    add_item("Skills:", "")
    skills_str = " • ".join(DATA["skills"])
    lines.append(f'<text x="100" y="{y-lh}" fill="{COLOR_TEXT}" font-family="monospace" font-size="13px">{escape_xml(skills_str)}</text>')
    
    y += 10
    add_item("Focus:", "")
    focus_str = " • ".join(DATA["focus"])
    lines.append(f'<text x="100" y="{y-lh}" fill="{COLOR_TEXT}" font-family="monospace" font-size="13px">{escape_xml(focus_str)}</text>')

    svg_height = y + 20
    
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 {svg_height}" width="480" height="{svg_height}">
<rect width="100%" height="100%" fill="{BG_COLOR}"/>
{''.join(lines)}
</svg>'''

    with open(output_path, "w") as f:
        f.write(svg_content)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_card()