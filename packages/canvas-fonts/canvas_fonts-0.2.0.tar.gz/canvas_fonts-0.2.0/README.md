# canvas_fonts

A Python library providing 200+ fonts for use in canvas editors like Fabric.js-based applications.

## Features

- 200+ carefully curated fonts from Google Fonts
- Organized into categories:
  - Sans-serif fonts (Roboto, Open Sans, etc.)
  - Serif fonts (Merriweather, Playfair Display, etc.)
  - Display fonts (Bebas Neue, Pacifico, etc.)
  - Monospace fonts (Source Code Pro, Fira Code, etc.)
  - Handwriting fonts (Dancing Script, Caveat, etc.)
  - Decorative fonts (Abril, Akronim, etc.)
- Easy-to-use API for font management
- Compatible with most canvas-based editors

## Installation

```bash
pip install canvas-fonts
```

## Usage

```python
from canvas_fonts import get_fonts, get_font_path

# List all available fonts
fonts = get_fonts()
print(fonts)  # Returns list of 200+ font names

# Get path to a specific font file
path = get_font_path("Roboto")
print(path)  # Returns absolute path to Roboto.ttf
```

## Font Categories

1. Sans-serif Fonts

   - Perfect for body text and UI elements
   - Includes: Roboto, Open Sans, Lato, Montserrat, and more

2. Serif Fonts

   - Ideal for headings and long-form content
   - Includes: Merriweather, Playfair Display, Lora, and more

3. Display Fonts

   - Great for headlines and attention-grabbing text
   - Includes: Bebas Neue, Pacifico, Dancing Script, and more

4. Monospace Fonts

   - Perfect for code snippets and technical content
   - Includes: Source Code Pro, Fira Code, JetBrains Mono, and more

5. Handwriting Fonts

   - Adds a personal touch to designs
   - Includes: Dancing Script, Caveat, Indie Flower, and more

6. Decorative Fonts
   - Ideal for special occasions and unique designs
   - Includes: Abril, Akronim, Aladin, and more

## License

MIT License - See LICENSE file for details.
