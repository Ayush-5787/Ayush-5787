import cv2
import numpy as np
import os

RAMP = " .`:-=+*cs#%@"  # Bright -> Dark
WIDTH_CHARS = 100
HEIGHT_CHARS = 53
FILL_COLOR = "#c9d1d9"  # GitHub dark mode text color
BG_COLOR = "#0d1117"    # GitHub dark mode bg

def generate_svg(image_path="data/source-prepped.png", output_path="avi-ascii.svg"):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"{image_path} not found. Run prep_photo.py first.")
        
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Resize to grid dimensions
    resized = cv2.resize(img, (WIDTH_CHARS, HEIGHT_CHARS), interpolation=cv2.INTER_AREA)
    
    rows = []
    char_height = 10 
    char_width = 6   
    
    svg_header = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH_CHARS * char_width} {(HEIGHT_CHARS + 2) * char_height}" width="{WIDTH_CHARS * char_width}" height="{(HEIGHT_CHARS + 2) * char_height}">
<style>
  @keyframes fadeIn {{
    from {{ opacity: 0; }}
    to {{ opacity: 1; }}
  }}
  text {{
    font-family: 'Courier New', Courier, monospace;
    font-size: {char_height}px;
    fill: {FILL_COLOR};
    white-space: pre;
  }}
  .row {{
    opacity: 0;
    animation: fadeIn 0.1s forwards;
  }}
</style>
<rect width="100%" height="100%" fill="{BG_COLOR}"/>
'''
    
    body_parts = []
    
    for r_idx in range(HEIGHT_CHARS):
        row_str = ""
        for c_idx in range(WIDTH_CHARS):
            val = resized[r_idx, c_idx]
            idx = int((val / 255) * (len(RAMP) - 1))
            row_str += RAMP[idx]
            
        safe_row = row_str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        delay = r_idx * 0.05 
        
        element = f'<g class="row" style="animation-delay: {delay}s;">'
        element += f'<text x="0" y="{(r_idx + 1) * char_height}">{safe_row}</text>'
        element += '</g>'
        body_parts.append(element)
        
    svg_footer = "</svg>"
    
    full_svg = svg_header + "\n".join(body_parts) + svg_footer
    
    with open(output_path, "w") as f:
        f.write(full_svg)
        
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_svg()