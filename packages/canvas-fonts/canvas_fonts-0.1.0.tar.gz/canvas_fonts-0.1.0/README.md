# canvas_fonts

A Python library providing 200+ fonts for use in canvas editors like Fabric.js-based applications.

## Installation

```bash
pip install canvas-fonts
```

## Usage

```python
from canvas_fonts import get_fonts, get_font_path

# List all fonts
fonts = get_fonts()
print(fonts)

# Get path to a font file
path = get_font_path("Roboto")
print(path)
```

## Adding Fonts

1. Download 200+ TTF files from Google Fonts or FontSquirrel (e.g., "Roboto.ttf", "Lobster.ttf")
2. Place them in `canvas_fonts/fonts/`
3. Update `FONTS` in `data.py` with all font names, ensuring they match the TTF filenames (without spaces, e.g., "OpenSans" for "Open Sans")

## License

MIT License - See LICENSE file for details.
