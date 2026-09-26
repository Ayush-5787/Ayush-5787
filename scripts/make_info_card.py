import os

DATA = {
    "name": "Ayush Nandan",
    "role": "AI & Full-Stack Developer",
    "edu": "B.Tech CSE · PSIT Kanpur",
    "loc": "Kanpur, India",
    "skills": ["Python", "React", "Node.js", "LangChain"]
}

def generate_card(output_path="info-card.svg"):
    # Simple HTML-like layout converted to valid SVG text elements
    lines = []
    y = 30
    lh = 25
    
    lines.append(f'<text x="20" y="{y}" fill="#58a6ff" font-weight="bold" font-family="sans-serif" font-size="18px">{DATA["name"]}</text>')
    y += lh
    lines.append(f'<text x="20" y="{y}" fill="#c9d1d9" font-family="sans-serif" font-size="14px">{DATA["role"]}</text>')
    y += lh + 10
    lines.append(f'<line x1="20" y1="{y}" x2="460" y2="{y}" stroke="#8b949e" stroke-width="1" opacity="0.3"/>')
    y += lh
    
    def add_line(label, value):
        nonlocal y
        lines.append(f'<text x="20" y="{y}" fill="#8b949e" font-family="monospace" font-size="13px">{label}</text>')
        lines.append(f'<text x="100" y="{y}" fill="#c9d1d9" font-family="monospace" font-size="13px">{value}</text>')
        y += lh

    add_line("Edu:", DATA["edu"])
    add_line("Loc:", DATA["loc"])
    y += 10
    add_line("Stack:", ", ".join(DATA["skills"]))

    height = y + 20
    
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 {height}" width="480" height="{height}">
<rect width="100%" height="100%" fill="#0d1117"/>
{''.join(lines)}
</svg>'''

    with open(output_path, "w") as f:
        f.write(svg_content)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_card()