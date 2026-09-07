"""Matplotlib rcParams, in two rendered sizes: print and talk.

Every size here is absolute (points), so a given piece of text comes out the
same height on the page no matter how wide the figure is. That is the right
invariant *within* one medium: all figures in a paper share a page, all figures
in a talk share a slide canvas. It does not carry *between* media. A 16:9 slide
canvas is 33.9 cm against a 16-18 cm text block, and is read from metres rather
than from arm's length, so slide figures need roughly twice the point size to
look the same. 8 pt on a slide subtends about half the angle that 10 pt body
text does on paper.

`get_params(scale)` builds one parameter set at a given scale, scaling every
point-valued entry (fonts, line widths, tick lengths, pads) by the same factor,
because scaling the text alone leaves hairline axes next to large labels.
`core.py` picks the scale from the figure-size key, so the `slide_*` presets
come out at 2x without the call site doing anything.

Layout
------
Constrained layout is on and the outer pad is zero, so the drawn content fills
the canvas exactly and the saved file is the width `figsize` asked for. Without
it, `savefig(bbox="tight")` trims the unused margin and the file comes out
5-20 % narrower than requested, by an amount that depends on how much label
text the figure happens to carry. Placing such a file at a fixed width scales
it back up, and the effective font size then varies from figure to figure,
which is precisely what the shared figure-size table exists to prevent.

`bbox="tight"` is kept as a safety net: with constrained layout it is a no-op
on the content, but if an artist is deliberately placed outside the canvas the
file grows to include it instead of clipping it silently. On top of it sits a
constant rim, `SAVEFIG_PAD_IN`, so nothing is flush against the edge of the
file or of a notebook cell. A constant pad is safe where `w_pad`/`h_pad` and
`tight_layout` are not: those change the content-to-canvas ratio by an amount
that depends on how much label text the figure carries, while this adds the
same 2 x pad to every figure, so two figures placed at one width still share
an effective point size.

Notes
-----
Calling `fig.tight_layout()` or `fig.subplots_adjust()` on a figure created
under these params warns and switches the figure back to the old behaviour.
Delete those calls; constrained layout already does the job.
"""

from typing import Any, Dict

# Print baseline. 8 pt at 40 cm reading distance subtends the same angle as
# 10 pt body text, and sits inside the 5-9 pt window publishers ask for.
BASE_FONT_SIZE = 8.0
BASE_WIDTH = 0.8

# Slide multiplier. 2x puts figure text at 16 pt on a 33.9 cm canvas, against
# 18-24 pt slide body text, and restores print-equivalent legibility at ~5 m.
SLIDE_SCALE = 2.0

DEFAULT_SCALE = 1.0

# Rim left around the figure by `savefig`, in inches at scale 1. Small enough to
# read as a margin rather than as whitespace, and scaled with everything else so
# a slide figure keeps the same proportion. `save_figure(..., pad=...)`
# overrides it per call; 0.0 restores a file trimmed flush to the content.
SAVEFIG_PAD_IN = 0.08

# Figure-size key prefix -> scale. Keys not listed here get `DEFAULT_SCALE`.
SCALE_BY_PREFIX: Dict[str, float] = {
    "slide": SLIDE_SCALE,
}


def scale_for_key(key: str) -> float:
    """Scale factor belonging to a figure-size key.

    Parameters
    ----------
    key : str
        A key from the figure-size table, e.g. `'double'` or `'slide_full'`.

    Returns
    -------
    float
        `SLIDE_SCALE` for `slide_*` keys, `DEFAULT_SCALE` otherwise.
    """
    prefix = key.split("_", 1)[0]
    return SCALE_BY_PREFIX.get(prefix, DEFAULT_SCALE)


def get_params(scale: float = DEFAULT_SCALE) -> Dict[str, Any]:
    """Build a full rcParams dict at a given scale.

    Parameters
    ----------
    scale : float, optional
        Multiplier applied to every point-valued entry. `1.0` (default) is the
        print set; `2.0` is the talk set. Sizes expressed in font-size units
        (the legend pads) are left alone, since they already follow the font.

    Returns
    -------
    dict of str to Any
        rcParams, ready for `matplotlib.pyplot.rcParams.update`. `figure.figsize`
        is not included; `core.py` adds it per figure-size key.

    Examples
    --------
    >>> plt.rcParams.update(get_params(SLIDE_SCALE))
    """

    def pt(value: float) -> float:
        """Scale a point-valued setting, rounded to something readable in a repr."""
        return round(value * scale, 2)

    return {
        # ----------------------------------------------------
        # figure
        # ----------------------------------------------------
        # "figure.figsize" is added in core.py, so update_params_string can
        # switch sizes without rebuilding the rest.
        "figure.dpi": 300,  # screen DPI (export handled by savefig)
        # Fill the canvas exactly, so the saved width is the requested width.
        "figure.constrained_layout.use": True,
        "figure.constrained_layout.w_pad": 0.0,
        "figure.constrained_layout.h_pad": 0.0,

        # ----------------------------------------------------
        # text
        # ----------------------------------------------------
        "font.family": "sans-serif",
        "font.sans-serif": ["Source Sans 3"],
        "font.size": pt(BASE_FONT_SIZE),

        # math text (honest + consistent)
        "mathtext.fontset": "custom",
        "mathtext.rm": "Source Serif 4",
        "mathtext.it": "Source Serif 4:italic",
        "mathtext.bf": "Source Serif 4:bold",

        "axes.unicode_minus": False,

        # ----------------------------------------------------
        # lines
        # ----------------------------------------------------
        "lines.linewidth": pt(1.2),
        "lines.markersize": pt(4),

        # ----------------------------------------------------
        # axes
        # ----------------------------------------------------
        "axes.linewidth": pt(BASE_WIDTH),
        "axes.titlesize": pt(9.5),  # slightly reduced -> matches font metrics
        "axes.labelsize": pt(9),
        "axes.labelpad": pt(8),  # tighter, avoids wasted vertical space

        # ----------------------------------------------------
        # ticks
        # ----------------------------------------------------
        "xtick.top": True,
        "ytick.right": True,

        # Tick labels match the base size; the axis label is one step up.
        "xtick.labelsize": pt(BASE_FONT_SIZE),
        "ytick.labelsize": pt(BASE_FONT_SIZE),

        "xtick.major.size": pt(3),
        "ytick.major.size": pt(3),

        "xtick.minor.size": pt(1.5),
        "ytick.minor.size": pt(1.5),

        "xtick.major.width": pt(BASE_WIDTH),
        "ytick.major.width": pt(BASE_WIDTH),

        "xtick.minor.width": pt(BASE_WIDTH),
        "ytick.minor.width": pt(BASE_WIDTH),

        "xtick.major.pad": pt(3),
        "ytick.major.pad": pt(3),

        "xtick.direction": "in",
        "ytick.direction": "in",

        # "xtick.minor.visible": True,
        # "ytick.minor.visible": True,

        # ----------------------------------------------------
        # grid
        # ----------------------------------------------------
        "axes.grid": False,
        "grid.color": "0.5",  # neutral gray, print-safe
        "grid.alpha": 0.2,
        "grid.linewidth": pt(0.4),

        # ----------------------------------------------------
        # legend
        # ----------------------------------------------------
        "legend.frameon": False,
        # Was 7 pt, at the floor of several publishers' minimum for no gain.
        # Matching the tick labels reads as one hierarchy.
        "legend.fontsize": pt(BASE_FONT_SIZE),
        # These three are in font-size units, so they scale on their own.
        "legend.handlelength": 2,
        "legend.handletextpad": 0.6,
        "legend.borderpad": 0.2,

        # ----------------------------------------------------
        # savefig
        # ----------------------------------------------------
        # A no-op under constrained layout, but it grows rather than clips if
        # an artist is placed outside the canvas on purpose.
        "savefig.bbox": "tight",
        # A thin rim, so nothing sits flush against the edge of the file or of
        # the cell output. Safe for the width invariant because it is a
        # *constant*: with constrained layout the tight bbox already equals the
        # canvas, so every figure grows by the same 2 x pad and placing two of
        # them at one width still gives them the same effective point size.
        # That is what separates it from `w_pad`/`h_pad`, which inset the
        # content and get trimmed straight back off, and from `tight_layout`,
        # which narrows the file by a content-dependent amount.
        "savefig.pad_inches": round(SAVEFIG_PAD_IN * scale, 3),
        "savefig.dpi": 300,
        "savefig.transparent": True,
        "savefig.format": "pdf",
    }


# The print set, kept as a module-level name for backwards compatibility.
BASE_PARAMS = get_params()
