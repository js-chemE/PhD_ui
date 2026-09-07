"""Shared figure sizes, keyed by target column width.

The table in `_assets/figsize.json` is stored in **centimetres**, because that
is how journal and template column widths are specified. Matplotlib's
`figsize` argument is in **inches**, so both accessors here default to
`in_metric=False` and hand back inches ready to pass straight to
`plt.subplots(figsize=...)`. Ask for `in_metric=True` only when you actually
want centimetres (e.g. to print a size, or to compare against a template).

The point of the table is that every figure destined for the same paper,
thesis chapter or talk shares one width, so nothing is rescaled on import and
font sizes stay consistent between figures.

Document keys are named for the target column width (`single_*` = 9 cm,
`double_*` = 18 cm) with the suffix setting the height. The `slide_*` keys use
the same grammar against the slide *body box*, the area left once the title
band and the margins are taken off a 16:9 canvas. Aspect ratio is deliberately
not part of the naming: one canvas is assumed, and the reason a slide key
exists at all is the 2x point size that goes with it, not the shape of the
deck.
"""

from pathlib import Path
from typing import Dict, Tuple

from phd_ui.plotting.conversion import cm_to_inches

module_dir = Path(__file__).resolve().parent.parent
asset_dir = module_dir / "_assets"

# Keys that existed before the 2026 rename, mapped to their current name. Only
# used to make the error message actionable -- these are NOT accepted as
# aliases, since silently honouring them is what let stale notebooks drift.
_RENAMED_KEYS = {
    "double_single_height": "double_single",
    "double_small": "double_short",
    "fullpage": "double_long",
    # The slide family stopped distinguishing 16:9 from 4:3 in 2026-09: both
    # decks are the same height and only the usable width differed, so the
    # keys now name how much of the slide the figure fills instead.
    "slide_16x9": "slide_full",
    "slide_4x3": "slide_full",
    "slide_tall": "slide_square",
}

# The slide canvas, in cm: PowerPoint 16:9 (13.333 x 7.5 in). The only key that
# uses it whole is `slide_full_16x9`.
SLIDE_CANVAS: Tuple[float, float] = (33.87, 19.05)

# What is left of that canvas once the title band and the margins are taken
# off, and the box every other `slide_*` key is cut from:
#
#     width   33.87 - 2 x 1.4 side margin              = 31.0
#     height  19.05 - 3.3 title band - 1.25 bottom     = 14.5
#
# The half width, `(31.0 - 2.0 gutter) / 2`, lands on 14.5 as well, so a
# half-width figure and a square one share a width and `slide_square` is
# genuinely square. `tests/test_figsize.py` checks that every slide key still
# fits in here, so the assumptions above cannot drift away from the table.
SLIDE_BODY: Tuple[float, float] = (31.0, 14.5)


class FigsizeKeyError(KeyError):
    """Unknown figure-size key.

    A `KeyError`, so `except KeyError` still catches it, but with `__str__`
    overridden: the base class reprs its argument, which would render the
    multi-line list of available keys as one line full of literal `\\n`.
    """

    def __str__(self) -> str:
        return self.args[0]


def get_figsizes(in_metric: bool = False) -> Dict[str, Tuple[float, float]]:
    """The whole figure-size table.

    Parameters
    ----------
    in_metric : bool, optional
        `False` (default) returns inches, ready for matplotlib. `True` returns
        the stored centimetres.

    Returns
    -------
    dict of str to (float, float)
        Key -> (width, height).
    """
    import json

    figsize_path = asset_dir / "figsize.json"
    with open(figsize_path, "r") as f:
        figsize = json.load(f)

    if in_metric:
        return {key: tuple(value) for key, value in figsize.items()}
    return {key: tuple(cm_to_inches(v) for v in value) for key, value in figsize.items()}


def get_figsize(key: str, in_metric: bool = False) -> Tuple[float, float]:
    """One figure size from the shared table.

    Parameters
    ----------
    key : str
        Table key, named for the target width: `single_*` = 9 cm (one journal
        column), `double_*` = 18 cm (full width), `slide_*` cut from the slide
        body box (`SLIDE_BODY`). The suffix sets the height.
    in_metric : bool, optional
        `False` (default) returns inches, ready for matplotlib. `True` returns
        the stored centimetres.

    Returns
    -------
    (float, float)
        Width and height.

    Raises
    ------
    KeyError
        If `key` is not in the table. The message lists every available key,
        and names the replacement if `key` is one that was renamed -- an
        unknown key is always a mistake, and used to degrade silently into
        matplotlib's default size instead of being caught.

    Examples
    --------
    >>> fig, ax = plt.subplots(figsize=get_figsize("double"))
    """
    figsize_dict = get_figsizes(in_metric=in_metric)
    if key in figsize_dict:
        return figsize_dict[key]

    unit = "cm" if in_metric else "in"
    available = "\n".join(
        f"    {name:<22} {w:6.2f} x {h:6.2f} {unit}"
        for name, (w, h) in figsize_dict.items()
    )
    hint = ""
    if key in _RENAMED_KEYS:
        hint = f"\n\n'{key}' was renamed to '{_RENAMED_KEYS[key]}'."
    raise FigsizeKeyError(
        f"'{key}' is not a figure-size key.{hint}\n\nAvailable keys:\n{available}"
    )
