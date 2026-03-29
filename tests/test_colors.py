from phd_ui import colors

def test_rgb_to_hex():
    rgb = (255, 0, 0)
    hex_color = colors.rgb_to_hex(rgb)
    assert hex_color == "#ff0000", f"Expected '#ff0000', got '{hex_color}'"

def test_hex_to_rgb():
    hex_color = "#00ff00"
    rgb = colors.hex_to_rgb(hex_color)
    assert rgb == (0, 255, 0), f"Expected (0, 255, 0), got {rgb}"