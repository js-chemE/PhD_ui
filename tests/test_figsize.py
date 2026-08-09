import pytest

from phd_ui.plotting.conversion import INCH2CM
from phd_ui.plotting.figsize import FigsizeKeyError, get_figsize, get_figsizes


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
