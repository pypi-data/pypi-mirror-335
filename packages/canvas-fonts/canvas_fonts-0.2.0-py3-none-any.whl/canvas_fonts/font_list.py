import os
from pathlib import Path
from .data import FONTS

PACKAGE_DIR = Path(__file__).parent
FONTS_DIR = PACKAGE_DIR / "fonts"

def get_fonts():
    """Return a list of available font names."""
    return FONTS

def get_font_path(font_name):
    """Return the absolute path to a font file."""
    if font_name not in FONTS:
        raise ValueError(f"Font '{font_name}' not found")
    font_file = f"{font_name.replace(' ', '')}.ttf"  # e.g., "Roboto.ttf"
    font_path = FONTS_DIR / font_file
    if not font_path.exists():
        raise FileNotFoundError(f"Font file for '{font_name}' not found at {font_path}")
    return str(font_path) 