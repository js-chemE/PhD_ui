"""
The Nature-branded colour palette, for drawings in Nature's house style.

Nature's art editors redraw every conceptual figure of a Reviews or News &
Views piece in this palette (``docs/natrev-artworkguide.pdf``). It is built
for **hierarchy**: two neutral *background* families for context, three
*main accent* families for the action, and an *extended* set for figures
that need to categorise or group elements. The guide's rules, in short:

- the most important element is the most saturated, weighted by
  significance, and background elements share one neutral tone;
- colour is used for hierarchy, for categorising, and for scientific or
  real-world conventions, never decoratively;
- black type, not coloured; no red/green pairs; check with a simulator.

The palette applies to conceptual figures, not data figures. Reach for it
when a drawing should look like it belongs in a Nature journal; the PhD
scheme (:mod:`phd_ui.colors.scheme`) stays the vocabulary for everything
else, and the plot colours come from there.

Provenance
----------
The hex values are those of ``nature-plot-style``
(https://github.com/hoanglongcao/nature-plot-style), picked from Nature's
own palette reference ``ncp.svg`` with Inkscape, so they are a close
reading of the printed swatches rather than official numbers. Each family
has six steps, lightest first. The steps are indexed 0 to 5 and the
*accent* of a family, the step that reads as "the" colour, is step 3.
"""

from matplotlib.colors import LinearSegmentedColormap

__all__ = [
    "NATURE",
    "NATURE_BACKGROUND",
    "NATURE_ACCENTS",
    "NATURE_EXTENDED",
    "NATURE_ACCENT_STEP",
    "nature_colors",
    "nature_cmap",
]

#: Every family of the palette, six steps from lightest to darkest.
NATURE: dict[str, tuple[str, ...]] = {
    "stone": ("#f7f5ef", "#e4e0ce", "#c6c2a6", "#a8a386", "#888366", "#625f4a"),
    "grey": ("#e6e6ed", "#c8ceda", "#99a3b4", "#6f7b91", "#49566d", "#253247"),
    "red": ("#fad0ce", "#eda4a7", "#de6866", "#c93e3f", "#9c2826", "#741915"),
    "blue": ("#c8e7fb", "#9dcbec", "#5799d1", "#0272b2", "#014e91", "#012c5c"),
    "yellow": ("#fff1c3", "#f6dc8a", "#ebc850", "#cca02c", "#9c7717", "#6b5513"),
    "olive": ("#f4f1b3", "#dfdc67", "#c9c700", "#9ba415", "#66771e", "#36461a"),
    "green": ("#d9e8c6", "#a0ca79", "#62b347", "#459434", "#227130", "#163b1c"),
    "teal": ("#cce7ee", "#97d2d4", "#4bbcbd", "#019aa3", "#016879", "#00394e"),
    "purple": ("#ebd6e9", "#d3aad1", "#bb7cb4", "#a84e94", "#792c74", "#481951"),
    "orange": ("#fde0bd", "#fbc07f", "#f59a45", "#ec6f00", "#b74f06", "#843200"),
    "skin": ("#f8e6d7", "#ddbda3", "#bf997d", "#936a57", "#755040", "#442d1f"),
}

#: The neutral families for contextual, background elements.
NATURE_BACKGROUND: tuple[str, ...] = ("stone", "grey")

#: The three main accent families, for the focus of a summary figure.
NATURE_ACCENTS: tuple[str, ...] = ("red", "blue", "yellow")

#: The extended palette, for categorising and grouping in complex or
#: multi-panel figures, in the order the guide prints it.
NATURE_EXTENDED: tuple[str, ...] = (
    "olive", "green", "teal", "blue", "purple", "red", "orange", "yellow", "skin",
)

#: The step of a family that reads as its accent colour.
NATURE_ACCENT_STEP: int = 3


def nature_colors(
    families: tuple[str, ...] | list[str] = NATURE_EXTENDED,
    step: int = NATURE_ACCENT_STEP,
) -> list[str]:
    """
    One hex colour per family at a given step, as a categorical list.

    Parameters
    ----------
    families : sequence of str, optional
        Family names in the wanted order. Default is the extended palette.
    step : int, optional
        Step within each family, 0 (lightest) to 5 (darkest). Default is
        the accent step.

    Returns
    -------
    list[str]
        Hex colours, one per family.

    Raises
    ------
    KeyError
        If a family name is unknown; the message lists the valid names.
    IndexError
        If `step` is outside 0 to 5.
    """
    if not 0 <= step <= 5:
        raise IndexError(f"step must be 0..5, got {step}")
    out = []
    for name in families:
        if name not in NATURE:
            raise KeyError(f"Unknown Nature family '{name}'. Available: {', '.join(NATURE)}")
        out.append(NATURE[name][step])
    return out


def nature_cmap(family: str, reverse: bool = False) -> LinearSegmentedColormap:
    """
    A family's six steps interpolated into a continuous colormap.

    Parameters
    ----------
    family : str
        Family name, e.g. ``'blue'``.
    reverse : bool, optional
        If True, run dark to light instead of light to dark.

    Returns
    -------
    LinearSegmentedColormap
        Colormap named ``nature_<family>`` (``_r`` suffixed when reversed).

    Raises
    ------
    KeyError
        If `family` is unknown; the message lists the valid names.
    """
    if family not in NATURE:
        raise KeyError(f"Unknown Nature family '{family}'. Available: {', '.join(NATURE)}")
    steps = list(NATURE[family])
    name = f"nature_{family}"
    if reverse:
        steps.reverse()
        name += "_r"
    return LinearSegmentedColormap.from_list(name, steps)
