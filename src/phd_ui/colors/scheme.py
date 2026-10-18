"""
The PhD colour scheme.

Ten hues, each in four fill tones and one line tone. The fill tones are
ordered light to dark: ``light``, the ``base`` that identifies the hue, a
``dark`` outline tone, and ``darkest`` for text on a light background.
``line`` is the tone for strokes and markers in a plot, see *Line tones*.

=========  ==========================================
key        hue
=========  ==========================================
pink       raspberry
orange     burnt orange
red        signal red
amber      amber
green      sea green
blue       sky blue
purple     violet
grey       cool grey
sand       warm sand (backgrounds, subtle notes)
ink        warm near-black (text & annotation)
=========  ==========================================

The green was not in the original drawing. It is built to match: its
hue (150°) sits in the wide gap between orange and blue, its saturation
(0.40–0.52) between purple's muted and orange's vivid, and its four
tones track blue's relative luminances to within 0.02.

Red and amber were added the same way: each keeps its own hue but its
four tones follow the mean light/dark ladder of green, blue and purple.
They give the two undesired species (CH4, CO) their own colours and so
leave ``orange`` free as a general marking / annotation hue.

Pink and orange came from the drawing with only ``base`` and ``dark``.
Their ``light`` and ``darkest`` were filled in (2026-10) from the mean
tone ladder of the five full families, measured in OKLCH: ``light`` is
``base`` lifted by 0.08 in lightness at 0.78 of its chroma, ``darkest``
is ``base`` dropped by 0.30 at 0.65 of its chroma, hue unchanged.

Sand is a warm neutral for backgrounds and low-priority annotations. It
is deliberately lighter and less saturated than grey at every tone, so
grey stays the colour for components while sand recedes: use
``sand.light`` as a subtle fill, ``sand.dark`` for its stroke and
``sand.darkest`` for text.

``INK`` is the black for text and annotation: its darkest tone is a soft
off-black, and a hint of warmth distinguishes it from the cool grey used
for fills. It is a full family and part of ``SCHEME`` like the rest, but
reach for it to write, not to fill.

Line tones
----------
The four tones above are fill tones. They were chosen on filled shapes in
a drawing, where Nature's rule for conceptual figures (most saturated for
the focus, neutral for the context, see ``docs/natrev-artworkguide.pdf``)
gives mid-chroma colours. A 1 pt line is a different stimulus: a thin
stroke is perceived less saturated and with less contrast than the same
colour as an area (the area effect of colour appearance), so a tone that
is right on a 2 cm box reads washed out as a plotted line. Blue and amber
``base`` were the clear cases, at 2.0:1 and 2.3:1 against white where
graphics need 3:1, with OKLCH chroma 0.09 to 0.12 where line palettes
(Tol vibrant, Petroff, tab10) sit at 0.13 to 0.22.

Every hue therefore carries a fifth tone, ``line``: the same hue, with
lightness pinned to 0.52-0.66 and chroma lifted to about 0.15 in OKLCH,
clipped to the sRGB gamut. Use it for lines and markers; fills keep
``base``. ``SCHEME_LINE`` is the categorical cycle built from the line
tones and is what ``axes.prop_cycle`` carries. Its order was found by
brute force to maximise the smallest adjacent colour distance under
normal, protan and deutan vision (OKLab dE x100: 17.6 normal, 9.2
simulated), so neighbouring series in a default-coloured plot stay apart.

Known limits: red, pink and orange sit within 41 degrees of hue, so any
two of them on one panel need a line style or a direct label as well.
Grey, sand and ink carry no chroma by design and separate by lightness
only; their ``line`` tones are the darkest tone that still reads as a
neutral line (grey a mid grey, sand its ``darkest``, ink its ``base``).

Colours are plain hex strings, so they can be handed straight to
Matplotlib or fed to :mod:`phd_ui.colors.cmaps` to build colormaps.
"""

from dataclasses import dataclass
from typing import Optional

__all__ = [
    "ColorFamily",
    "SCHEME",
    "SCHEME_COLORS",
    "SCHEME_LINE",
    "PINK",
    "ORANGE",
    "RED",
    "AMBER",
    "GREEN",
    "BLUE",
    "PURPLE",
    "GREY",
    "SAND",
    "INK",
    "get_family",
]


@dataclass(frozen=True)
class ColorFamily:
    """
    One hue of the PhD colour scheme, in up to four tones.

    Every hue shipped in :data:`SCHEME` defines all four; `light` and
    `darkest` are optional only so a caller can build a partial family.

    Parameters
    ----------
    name : str
        Hue key, e.g. ``'blue'``.
    base : str
        The tone that identifies the hue. Use it for the main line,
        marker or patch.
    dark : str
        A darker tone of `base`. Works as an edge colour, or as a
        second series.
    light : str or None, optional
        A lighter tone of `base`, for fills and bands.
    darkest : str or None, optional
        The darkest tone, dark enough to read as text on white or on
        `light`.
    line : str or None, optional
        The tone for lines and markers in a plot: same hue, more chroma,
        mid lightness. Falls back to `dark` when unset.
    """

    name: str
    base: str
    dark: str
    light: Optional[str] = None
    darkest: Optional[str] = None
    line: Optional[str] = None

    def __post_init__(self) -> None:
        if self.line is None:
            object.__setattr__(self, "line", self.dark)

    @property
    def shades(self) -> list[str]:
        """
        The hue's fill tones, light to dark. `line` is not among them.

        Returns
        -------
        list[str]
            ``[light, base, dark, darkest]`` with any undefined tone
            dropped, so a partial family gives fewer than four entries.
        """
        ordered = [self.light, self.base, self.dark, self.darkest]
        return [c for c in ordered if c is not None]

    def __str__(self) -> str:
        return self.base


PINK = ColorFamily(
    name="pink",
    base="#c94c7b",
    dark="#7b2b49",
    light="#d67394",
    darkest="#530b2b",
    line="#c93f76",
)

ORANGE = ColorFamily(
    name="orange",
    base="#d55b2a",
    dark="#903d1f",
    light="#e1805d",
    darkest="#5a1b00",
    line="#db551a",
)

RED = ColorFamily(
    name="red",
    base="#c05449",
    dark="#6a302a",
    light="#cf7d75",
    darkest="#4f1d17",
    line="#c44036",
)

AMBER = ColorFamily(
    name="amber",
    base="#cfa44b",
    dark="#7d6128",
    light="#dbbb7a",
    darkest="#624915",
    line="#ba8904",
)

GREEN = ColorFamily(
    name="green",
    base="#42a975",
    dark="#29704f",
    light="#7bc6a1",
    darkest="#184e37",
    line="#02985f",
)

BLUE = ColorFamily(
    name="blue",
    base="#6fc1e4",
    dark="#306f8e",
    light="#83c0e9",
    darkest="#1e485c",
    line="#0186ae",
)

PURPLE = ColorFamily(
    name="purple",
    base="#6863ac",
    dark="#39375f",
    light="#908cc4",
    darkest="#27265f",
    line="#6353c5",
)

GREY = ColorFamily(
    name="grey",
    base="#9aa1ac",
    dark="#5e6570",
    light="#c3c8cf",
    darkest="#3f4245",
    line="#79818c",
)

SAND = ColorFamily(
    name="sand",
    base="#e3dfd8",
    dark="#aca08b",
    light="#f4f3f1",
    darkest="#827359",
    line="#827359",
)

#: The ink / "black" family: for writing and annotating, not for fills.
#: Its darkest tone is a soft off-black (not pure #000, which reads harsh),
#: and a hint of warmth sets it apart from the cool, lighter ``grey`` used
#: to fill components. Use ``INK.darkest`` for headings, ``INK.base`` for
#: body text, ``INK.light`` for secondary / captions.
INK = ColorFamily(
    name="ink",
    base="#413b34",
    dark="#2e2924",
    light="#675f56",
    darkest="#1d1a16",
    line="#413b34",
)

SCHEME: dict[str, ColorFamily] = {
    f.name: f for f in (PINK, ORANGE, RED, AMBER, GREEN, BLUE, PURPLE, GREY, SAND, INK)
}

#: Categorical fill palette: one base tone per hue, in scheme order.
SCHEME_COLORS: list[str] = [f.base for f in SCHEME.values()]

#: Categorical line palette and the default ``axes.prop_cycle``: the line
#: tones of the eight chromatic hues plus grey, in the order that keeps
#: neighbouring entries furthest apart under normal and colour-deficient
#: vision (see the module docstring). Sand and ink are not series colours.
SCHEME_LINE: list[str] = [
    SCHEME[k].line for k in ("blue", "orange", "green", "purple", "pink", "amber", "red", "grey")
]


def get_family(name: str) -> ColorFamily:
    """
    Look up a hue by name.

    Parameters
    ----------
    name : str
        Hue key, case-insensitive: one of ``'pink'``, ``'orange'``,
        ``'red'``, ``'amber'``, ``'green'``, ``'blue'``, ``'purple'``,
        ``'grey'``, ``'sand'``, ``'ink'``.

    Returns
    -------
    ColorFamily
        The requested hue.

    Raises
    ------
    KeyError
        If `name` is not a known hue; the message lists the valid keys.
    """
    key = name.strip().lower()
    if key not in SCHEME:
        raise KeyError(
            f"Unknown colour '{name}'. Available: {', '.join(SCHEME)}"
        )
    return SCHEME[key]
