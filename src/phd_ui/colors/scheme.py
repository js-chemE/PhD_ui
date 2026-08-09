"""
The PhD colour scheme.

Eight hues, each in two to four tones. The tones are ordered light to
dark: an optional ``light``, the ``base`` that identifies the hue, a
``dark`` outline tone, and an optional ``darkest`` for text on a light
background.

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
=========  ==========================================

The green was not in the original drawing. It is built to match: its
hue (150°) sits in the wide gap between orange and blue, its saturation
(0.40–0.52) between purple's muted and orange's vivid, and its four
tones track blue's relative luminances to within 0.02.

Red and amber were added the same way: each keeps its own hue but its
four tones follow the mean light/dark ladder of green, blue and purple.
They give the two undesired species (CH4, CO) their own colours and so
leave ``orange`` free as a general marking / annotation hue.

Colours are plain hex strings, so they can be handed straight to
Matplotlib or fed to :mod:`phd_ui.colors.cmaps` to build colormaps.
"""

from dataclasses import dataclass
from typing import Optional

__all__ = [
    "ColorFamily",
    "SCHEME",
    "SCHEME_COLORS",
    "PINK",
    "ORANGE",
    "RED",
    "AMBER",
    "GREEN",
    "BLUE",
    "PURPLE",
    "GREY",
    "INK",
    "get_family",
]


@dataclass(frozen=True)
class ColorFamily:
    """
    One hue of the PhD colour scheme, in two to four tones.

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
        A lighter tone of `base`, defined only for `blue` and `purple`.
    darkest : str or None, optional
        The darkest tone, dark enough to read as text on white or on
        `light`. Not defined for every hue.
    """

    name: str
    base: str
    dark: str
    light: Optional[str] = None
    darkest: Optional[str] = None

    @property
    def shades(self) -> list[str]:
        """
        The hue's tones, light to dark.

        Returns
        -------
        list[str]
            ``[light, base, dark, darkest]`` with the undefined tones
            dropped, so the result has between two and four entries.
        """
        ordered = [self.light, self.base, self.dark, self.darkest]
        return [c for c in ordered if c is not None]

    def __str__(self) -> str:
        return self.base


PINK = ColorFamily(
    name="pink",
    base="#c94c7b",
    dark="#7b2b49",
)

ORANGE = ColorFamily(
    name="orange",
    base="#d55b2a",
    dark="#903d1f",
)

RED = ColorFamily(
    name="red",
    base="#c0392b",
    dark="#5c201a",
    light="#d75c4f",
    darkest="#3e0f0b",
)

AMBER = ColorFamily(
    name="amber",
    base="#e1a72e",
    dark="#805f1a",
    light="#e8bc62",
    darkest="#644609",
)

GREEN = ColorFamily(
    name="green",
    base="#42a975",
    dark="#29704f",
    light="#7bc6a1",
    darkest="#184e37",
)

BLUE = ColorFamily(
    name="blue",
    base="#6fc1e4",
    dark="#306f8e",
    light="#83c0e9",
    darkest="#1e485c",
)

PURPLE = ColorFamily(
    name="purple",
    base="#6863ac",
    dark="#39375f",
    light="#908cc4",
    darkest="#27265f",
)

GREY = ColorFamily(
    name="grey",
    base="#9aa1ac",
    dark="#5e6570",
    darkest="#3f4245",
)

#: Neutral grey for arrows, annotations and anything that should not
#: carry a hue.
INK = "#5e646f"

SCHEME: dict[str, ColorFamily] = {
    f.name: f for f in (PINK, ORANGE, RED, AMBER, GREEN, BLUE, PURPLE, GREY)
}

#: Categorical palette: one base tone per hue.
SCHEME_COLORS: list[str] = [f.base for f in SCHEME.values()]


def get_family(name: str) -> ColorFamily:
    """
    Look up a hue by name.

    Parameters
    ----------
    name : str
        Hue key, case-insensitive: one of ``'pink'``, ``'orange'``,
        ``'red'``, ``'amber'``, ``'green'``, ``'blue'``, ``'purple'``,
        ``'grey'``.

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
