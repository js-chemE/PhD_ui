"""Slides scale line widths by SLIDE_LINE_SCALE, text by SLIDE_SCALE (set 2026-10-26)."""

import pytest

from phd_ui.plotting import PARAMS, SLIDE_LINE_SCALE, SLIDE_SCALE, line_scale_for_key, scale_for_key
from phd_ui.sketch.scene import Scene


def test_factors():
    assert line_scale_for_key("slide_half") == SLIDE_LINE_SCALE
    assert line_scale_for_key("double") == 1.0
    assert scale_for_key("slide") == SLIDE_SCALE


@pytest.mark.parametrize("key", ["slide", "slide_half", "slide_full"])
def test_slide_lines_heavier_than_text(key):
    print_, slide = PARAMS["double"], PARAMS[key]
    assert slide["lines.linewidth"] == pytest.approx(print_["lines.linewidth"] * SLIDE_LINE_SCALE)
    assert slide["axes.linewidth"] == pytest.approx(print_["axes.linewidth"])          # frame stays at print width
    assert slide["xtick.major.width"] == pytest.approx(print_["xtick.major.width"])
    assert slide["font.size"] == pytest.approx(print_["font.size"] * SLIDE_SCALE)


def test_scene_line_scale():
    sc = Scene.from_figsize("slide", pm_per_mm=30)
    assert sc.lw(1.0) / sc.pt(1.0) == pytest.approx(SLIDE_LINE_SCALE / SLIDE_SCALE)
    assert Scene(10, 10).lw(1.0) == pytest.approx(Scene(10, 10).pt(1.0))
