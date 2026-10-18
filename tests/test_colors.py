import re
import subprocess
import sys

import matplotlib.pyplot as plt
import pytest

from phd_ui import colors
from phd_ui.colors.scheme import SCHEME, SCHEME_LINE
from phd_ui.plotting import update_params_string

HEX = re.compile(r"^#[0-9a-f]{6}$", re.IGNORECASE)

TONES = ("light", "base", "dark", "darkest", "line")


def _relative_luminance(hex_color: str) -> float:
    rgb = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def _contrast_on_white(hex_color: str) -> float:
    return 1.05 / (_relative_luminance(hex_color) + 0.05)


def test_rgb_to_hex():
    rgb = (255, 0, 0)
    hex_color = colors.rgb_to_hex(rgb)
    assert hex_color == "#ff0000", f"Expected '#ff0000', got '{hex_color}'"


def test_hex_to_rgb():
    hex_color = "#00ff00"
    rgb = colors.hex_to_rgb(hex_color)
    assert rgb == (0, 255, 0), f"Expected (0, 255, 0), got {rgb}"


# ---------------------------------------------------------------- scheme

def test_every_family_defines_every_tone():
    for family in SCHEME.values():
        for tone in TONES:
            value = getattr(family, tone)
            assert value is not None, f"{family.name}.{tone} is undefined"
            assert HEX.match(value), f"{family.name}.{tone} = {value!r} is not a hex colour"
        assert len(family.shades) == 4


def test_fill_tones_run_light_to_dark():
    for family in SCHEME.values():
        lum = [_relative_luminance(c) for c in family.shades]
        assert lum == sorted(lum, reverse=True), f"{family.name} tones are not ordered light to dark"


def test_line_tones_read_on_white():
    """A plotted line needs 3:1 against the page; the fill tones need not."""
    for family in SCHEME.values():
        ratio = _contrast_on_white(family.line)
        assert ratio >= 3.0, f"{family.name}.line has {ratio:.1f}:1 contrast on white"


def test_line_tone_falls_back_to_dark():
    partial = colors.ColorFamily(name="x", base="#aaaaaa", dark="#555555")
    assert partial.line == "#555555"
    assert partial.shades == ["#aaaaaa", "#555555"]


def test_scheme_line_cycle():
    assert len(SCHEME_LINE) == 8
    assert len(set(SCHEME_LINE)) == 8
    line_tones = {f.line for f in SCHEME.values()}
    assert set(SCHEME_LINE) <= line_tones
    assert SCHEME_LINE[0] == colors.BLUE.line
    assert colors.SAND.line not in SCHEME_LINE
    assert colors.INK.line not in SCHEME_LINE


def test_get_family_is_case_insensitive_and_strict():
    assert colors.get_family(" Blue ") is colors.BLUE
    with pytest.raises(KeyError):
        colors.get_family("teal")


# ---------------------------------------------------------------- species

def test_species_have_line_and_fill_colours():
    for name, species in colors.SPECIES.items():
        assert HEX.match(species.color), name
        assert HEX.match(species.fill), name
        if species.family is not None:
            family = SCHEME[species.family]
            assert species.color in {getattr(family, t) for t in TONES}, name
            assert species.fill in family.shades, name
    assert colors.SPECIES_COLORS == {n: s.color for n, s in colors.SPECIES.items()}
    assert colors.SPECIES_FILL_COLORS == {n: s.fill for n, s in colors.SPECIES.items()}


def test_species_sharing_a_hue_differ_in_colour():
    by_family: dict[str, list[str]] = {}
    for species in colors.SPECIES.values():
        if species.family is not None:
            by_family.setdefault(species.family, []).append(species.color)
    for family, members in by_family.items():
        assert len(members) == len(set(members)), f"{family} species share a line colour"


def test_species_line_colours_read_on_white():
    for name, hex_color in colors.SPECIES_COLORS.items():
        assert _contrast_on_white(hex_color) >= 3.0, name


# ---------------------------------------------------------------- nature

def test_nature_palette_shape():
    assert len(colors.NATURE) == 11
    for name, steps in colors.NATURE.items():
        assert len(steps) == 6, name
        assert all(HEX.match(c) for c in steps), name
        lum = [_relative_luminance(c) for c in steps]
        assert lum == sorted(lum, reverse=True), f"nature {name} is not ordered light to dark"
    groups = set(colors.NATURE_BACKGROUND) | set(colors.NATURE_ACCENTS) | set(colors.NATURE_EXTENDED)
    assert groups == set(colors.NATURE)


def test_nature_colors_and_cmap():
    picked = colors.nature_colors()
    assert len(picked) == len(colors.NATURE_EXTENDED)
    assert picked[0] == colors.NATURE["olive"][colors.NATURE_ACCENT_STEP]
    assert colors.nature_colors(("red",), step=0) == [colors.NATURE["red"][0]]
    cmap = colors.nature_cmap("blue")
    assert cmap.name == "nature_blue"
    assert colors.nature_cmap("blue", reverse=True).name == "nature_blue_r"
    with pytest.raises(KeyError):
        colors.nature_colors(("cyan",))
    with pytest.raises(IndexError):
        colors.nature_colors(step=6)


# ---------------------------------------------------------------- rcParams

def test_prop_cycle_is_the_scheme_line_cycle():
    update_params_string("single")
    cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    assert cycle == SCHEME_LINE
    update_params_string("slide")
    assert plt.rcParams["axes.prop_cycle"].by_key()["color"] == SCHEME_LINE


@pytest.mark.parametrize("module", ["phd_ui.colors", "phd_ui.plotting", "phd_ui.colors.scheme", "phd_ui"])
def test_import_order_is_free_of_cycles(module: str):
    """params imports the scheme and preview imports plotting; either side must import first."""
    result = subprocess.run(
        [sys.executable, "-c", f"import {module}"],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stderr


# ---------------------------------------------------------------- atoms and bonds

def _lightness(hex_color: str) -> float:
    return _relative_luminance(hex_color) ** (1 / 3)


def test_atoms_are_complete_and_ordered():
    for symbol, atom in colors.ATOMS.items():
        for tone in (atom.fill, atom.edge, atom.light, atom.text):
            assert HEX.match(tone), (symbol, tone)
        assert atom.radius_pm > 0, symbol
        assert _relative_luminance(atom.edge) < _relative_luminance(atom.fill), f"{symbol} edge not darker"
        assert _relative_luminance(atom.light) >= _relative_luminance(atom.fill), f"{symbol} light not lighter"


def test_cpk_conventions_hold():
    a = colors.ATOMS
    assert a["O"].fill == colors.RED.line
    assert a["P"].fill == colors.ORANGE.line            # CPK: phosphorus orange
    assert a["C"].fill == colors.GREY.darkest           # dark grey, not black
    assert _relative_luminance(a["C"].fill) > 0.03      # well clear of #000
    assert _relative_luminance(a["H"].fill) > 0.85      # white
    s_luminance = _relative_luminance(a["S"].fill)
    assert s_luminance > _relative_luminance(a["P"].fill)   # sulfur the light yellow


def test_bond_styles_and_lengths():
    assert set(colors.BOND_STYLES) == {"single", "double", "triple", "partial", "surface"}
    assert [colors.BOND_STYLES[k].lines for k in ("single", "double", "triple")] == [1, 2, 3]
    assert colors.bond_length_pm("C", "O") == 76 + 66
    with pytest.raises(KeyError):
        colors.get_atom("Xx")


def test_draw_molecule_layers_atoms_over_bonds():
    from phd_ui.plotting import draw_molecule

    fig, ax = plt.subplots()
    ax.set_aspect("equal")
    draw_molecule(ax, [("O", -132, 0), ("C", 0, 0), ("O", 132, 0)], [(0, 1, "double"), (1, 2, "double")])
    assert len(ax.patches) == 3
    assert len(ax.lines) == 4                            # two double bonds
    assert min(p.get_zorder() for p in ax.patches) > max(l.get_zorder() for l in ax.lines)
    plt.close(fig)


def test_wong_palette_matches_the_paper():
    assert colors.WONG["orange"] == "#e69f00"            # 230, 159, 0
    assert colors.WONG["bluish green"] == "#009e73"      # 0, 158, 115
    assert colors.WONG["reddish purple"] == "#cc79a7"    # 204, 121, 167
    assert len(colors.WONG) == 8
    assert colors.WONG_COLORS[-1] == "#000000"


def test_h2_and_ch4_stay_apart():
    """H2 and CH4 share the red hue; lightness has to carry them apart."""
    h2, ch4 = colors.SPECIES["H2"].color, colors.SPECIES["CH4"].color
    assert _contrast_on_white(h2) >= 3.0
    assert _relative_luminance(h2) / _relative_luminance(ch4) > 2.5
