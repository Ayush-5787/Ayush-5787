"""
prep_photo.py — one-time photo prep for the ASCII portrait pipeline.

A flatly-lit face converts to a dark, unreadable blob if you skip this step.
Three fixes, in order:
  1. Remove the background (rembg) so only the subject remains.
  2. Boost local contrast with CLAHE so a flat face gets real highlights/shadows.
  3. Composite onto pure white, so the background maps to the blank end of
     the ASCII ramp (white -> space character) instead of printing as noise.

Run this once per photo -- NOT part of the daily automation.

Usage:
    python scripts/prep_photo.py source-photo.jpg [source-prepped.png]
"""
import io
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def remove_background(raw_bytes: bytes) -> Image.Image:
    """Return an RGBA PIL image with the background removed via rembg."""
    from rembg import remove  # imported lazily: heavy, portrait-only dependency

    result = remove(raw_bytes)
    return Image.open(io.BytesIO(result)).convert("RGBA")


def composite_on_white(rgba: Image.Image) -> Image.Image:
    """Flatten an RGBA cutout onto a pure white background."""
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    return Image.alpha_composite(white_bg, rgba).convert("RGB")


def apply_clahe(gray: np.ndarray) -> np.ndarray:
    """Contrast-Limited Adaptive Histogram Equalization.

    clipLimit keeps noise from blowing out in flat regions; tileGridSize
    controls how local the equalization is (smaller tiles = more local detail).
    """
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    return clahe.apply(gray)


def prep_photo(src_path: str, out_path: str = "source-prepped.png") -> None:
    src = Path(src_path)
    if not src.exists():
        raise FileNotFoundError(f"Source photo not found: {src_path}")

    raw = src.read_bytes()

    print("Removing background...")
    subject_rgba = remove_background(raw)

    print("Compositing onto white...")
    on_white = composite_on_white(subject_rgba)

    print("Boosting local contrast (CLAHE)...")
    gray = cv2.cvtColor(np.array(on_white), cv2.COLOR_RGB2GRAY)
    contrasted = apply_clahe(gray)

    Image.fromarray(contrasted).save(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <source-photo> [output.png]")
        sys.exit(1)
    out = sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png"
    prep_photo(sys.argv[1], out)