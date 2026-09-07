import pytest

from phd_ui.plotting.conversion import INCH2CM
from phd_ui.plotting.figsize import (
    SLIDE_BODY,
    SLIDE_CANVAS,
    FigsizeKeyError,
    get_figsize,
    get_figsizes,
)
from phd_ui.plotting.params import SLIDE_SCALE, scale_for_key


def test_default_is_inches():
    """The table is stored in cm, but matplotlib wants inches, so inches is
    the default -- getting this backwards silently produces a figure 2.54x
    too large in each dimension."""
    cm = get_figsize("double", in_metric=True)
    inches = get_figsize("double")
    assert cm == (18, 11.5)
    assert inches == pytest.approx((18 / INCH2CM, 11.5 / INCH2CM))
    assert get_figsize("double", in_metric=False) == inches


def test_get_figsizes_default_matches_get_figsize():
    table = get_figsizes()
    assert table["double"] == get_figsize("double")
    assert get_figsizes(in_metric=True)["double"] == (18, 11.5)


def test_every_key_is_a_positive_pair():
    for key, value in get_figsizes(in_metric=True).items():
        assert len(value) == 2, key
        assert all(v > 0 for v in value), key


def test_unknown_key_raises_and_lists_the_alternatives():
    """An unknown key used to warn and fall back to matplotlib's default size,
    so a typo silently produced a wrongly-sized figure."""
    with pytest.raises(KeyError) as excinfo:
        get_figsize("definitely_not_a_key")
    message = str(excinfo.value)
    assert "definitely_not_a_key" in message
    for key in get_figsizes():
        assert key in message


def test_renamed_key_names_its_replacement():
    with pytest.raises(FigsizeKeyError) as excinfo:
        get_figsize("double_single_height")
    assert "renamed to 'double_single'" in str(excinfo.value)


def test_error_is_catchable_as_keyerror_and_prints_multiline():
    """FigsizeKeyError subclasses KeyError so `except KeyError` still works,
    but overrides __str__ -- KeyError's default reprs its argument, which
    would collapse the key list onto one line full of literal \\n."""
    assert issubclass(FigsizeKeyError, KeyError)
    with pytest.raises(KeyError) as excinfo:
        get_figsize("nope")
    assert "\n" in str(excinfo.value)
    assert "\\n" not in str(excinfo.value)


def test_widths_are_grouped_by_target_column():
    table = get_figsizes(in_metric=True)
    assert {w for k, (w, _) in table.items() if k.startswith("single")} == {9}
    assert {w for k, (w, _) in table.items() if k.startswith("double")} == {18}


def test_slide_keys_fit_the_slide_body_box():
    """Every slide preset except the full-bleed one is cut from the body box,
    the area left under the title band. A key that overflowed it would be
    silently shrunk on import, which is the whole thing the table prevents."""
    table = get_figsizes(in_metric=True)
    body_width, body_height = SLIDE_BODY
    for key, (width, height) in table.items():
        if not key.startswith("slide") or key == "slide_full_16x9":
            continue
        assert width <= body_width, key
        assert height <= body_height, key


def test_slide_full_bleed_is_the_whole_canvas():
    assert get_figsize("slide_full_16x9", in_metric=True) == SLIDE_CANVAS


def test_slide_widths_are_the_body_box_and_its_half():
    """Half of the body width lands on the body height, so a half-width slide
    figure and a square one share a width and `slide_square` is square."""
    table = get_figsizes(in_metric=True)
    body_width, body_height = SLIDE_BODY
    widths = {
        w for k, (w, _) in table.items()
        if k.startswith("slide") and k != "slide_full_16x9"
    }
    assert widths == {body_width, body_height}
    assert get_figsize("slide_square", in_metric=True) == (body_height, body_height)
    assert get_figsize("slide_full", in_metric=True) == SLIDE_BODY


def test_dropped_aspect_keys_name_their_replacement():
    """16:9 and 4:3 decks are the same height and differed only in usable
    width, so the aspect no longer appears in the names."""
    for old, new in [
        ("slide_16x9", "slide_full"),
        ("slide_4x3", "slide_full"),
        ("slide_tall", "slide_square"),
    ]:
        with pytest.raises(FigsizeKeyError) as excinfo:
            get_figsize(old)
        assert f"renamed to '{new}'" in str(excinfo.value)


def test_slide_keys_carry_the_talk_scale():
    """The point of a slide key is the 2x point size that comes with it, so
    every one of them must resolve to `SLIDE_SCALE`, the new names included."""
    for key in get_figsizes():
        expected = SLIDE_SCALE if key.startswith("slide") else 1.0
        assert scale_for_key(key) == expected, key
