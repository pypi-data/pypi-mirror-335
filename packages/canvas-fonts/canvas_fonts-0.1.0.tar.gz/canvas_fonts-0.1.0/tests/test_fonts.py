import pytest
from canvas_fonts import get_fonts, get_font_path

def test_get_fonts():
    fonts = get_fonts()
    assert len(fonts) >= 20  # Update to 200+ when complete
    assert "Roboto" in fonts

def test_get_font_path():
    path = get_font_path("Roboto")
    assert path.endswith("Roboto.ttf")
    with pytest.raises(ValueError):
        get_font_path("UnknownFont") 