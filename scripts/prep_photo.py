import cv2
import numpy as np
from rembg import remove, new_session
from PIL import Image
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <input_image>")
        return
    
    input_path = sys.argv[1]
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "source-prepped.png")
    
    print(f"Processing {input_path}...")
    
    # Load image
    img = Image.open(input_path)
    
    # Create a session with the LITE model (u2netp) to save RAM
    print("Loading lite model (u2netp)...")
    session = new_session("u2netp")
    
    # Remove background using AI
    print("Removing background (this may take a moment)...")
    img_no_bg = remove(img, session=session)
    
    # Convert to grayscale
    gray = cv2.cvtColor(np.array(img_no_bg.convert('RGB')), cv2.COLOR_RGB2GRAY)
    
    # Apply CLAHE for contrast
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Composite onto white so background maps to spaces in ASCII
    height, width = enhanced.shape
    white_canvas = np.ones((height, width), dtype=np.uint8) * 255
    
    # Mask where original had alpha > 0 (subject)
    mask = np.array(img_no_bg.split()[3]) > 0
    
    result = white_canvas.copy()
    result[mask] = enhanced[mask]
    
    cv2.imwrite(output_path, result)
    print(f"Saved prepped image to {output_path}")

if __name__ == "__main__":
    main()
