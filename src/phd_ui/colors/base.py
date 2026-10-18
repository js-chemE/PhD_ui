"""
Per-species colours, derived from the PhD colour scheme.

The scheme (:mod:`phd_ui.colors.scheme`) is the shared vocabulary for
schematics and drawings. Species reuse the *same* hues, but here the hue
encodes the species' **role on a desirability axis**, so a plot's colours
also carry meaning rather than just identity:

    ============  ==============  =====================================
    hue           role            species
    ============  ==============  =====================================
    green         target product  MeOH  ("green methanol")
    blue / red    feed            CO2 (dark blue), H2 (light red)
    purple/pink   side product    EtOH (purple), MF, DME (pink)
    red / amber   undesired       CH4 (red, worst), CO (amber)
    ocean         water           H2O
    grey          inert           Ar, He, N2
    ============  ==============  =====================================

This is a desirability gradient: cool = wanted, warm = not. The side
products run from EtOH (purple, nearest the green target, being a valuable
alcohol like methanol) through MF to DME (pink, nearest the undesired end).
The two undesired species get their own warm hues -- CH4 a deep red as
the worst, CO an amber -- which keeps the scheme's **orange free as a
general marking / annotation colour**. Water is the one deliberate
exception: a literal **ocean blue**, because H2O reads as blue.

H2 is the other exception to cool = wanted (2026-10-18): it is the light
red, ``RED.light``. The two feeds are what a switching experiment
alternates, and blue against red is the strongest pair that survives
colour blindness (blue against a yellowish tone for a deuteranope); it is
also how gas-switching figures in the literature shade the two halves
(Gomez et al., ACS Catal. 2024, Fig. 5). H2 and CH4 share the red hue and
differ in lightness: H2 is the light ``RED.light`` and CH4 a deep red of its
own, :data:`METHANE` (OKLCH L 0.44, C 0.17), darker than every red tone a
line takes but as saturated. That puts them OKLab dE 24 apart (23 under
deuteranopia), against 13 when CH4 was ``RED.line``; it was the widest gap a
search over both tones found that kept H2 at 3:1 on white and both clear of
MF, DME, CO, CO2 and MeOH (nearest: CH4 to DME at 9). It also moved CH4
away from MeOH, the worst red-green pair before (5.6 under deuteranopia).
Like the ocean blue, METHANE is a species literal, not a scheme tone, so
``RED.line`` (the line cycle, oxygen) is untouched.

Line and fill
-------------
Each species carries two colours. ``color`` is the one a plot uses for a
trace or a marker: the hue's ``line`` tone, or a darker fill tone where two
species share a hue and have to be told apart by lightness (CO2 next to H2,
DME next to MF, the three inerts). ``fill`` is the drawing tone, the hue's
``base``, ``dark`` or ``darkest`` as before, for filled shapes, bands and
schematics. Lines and fills of one species then share a hue, so a trace and
the box it is drawn from read as the same thing. See *Line tones* in
:mod:`phd_ui.colors.scheme` for why a line needs more chroma than a fill.

Because the colours are looked up from the scheme, editing a scheme hue
moves every species of that role with it. ``SPECIES_COLORS`` keeps the
historical ``{name: hex}`` shape and holds the line colours;
``SPECIES_FILL_COLORS`` the fills; ``SPECIES`` and ``SPECIES_ROLES`` expose
the richer structure.
"""

from dataclasses import dataclass
from typing import Optional

from phd_ui.colors.scheme import (
    AMBER,
    BLUE,
    GREEN,
    GREY,
    PINK,
    PURPLE,
    RED,
    ColorFamily,
)

__all__ = ["Species", "SPECIES", "SPECIES_COLORS", "SPECIES_FILL_COLORS", "SPECIES_ROLES"]


@dataclass(frozen=True)
class Species:
    """
    One chemical species and the colours it is drawn in.

    Parameters
    ----------
    name : str
        Species abbreviation, e.g. ``'MeOH'``.
    color : str
        Hex colour for lines and markers, resolved from the scheme (or a
        literal for water).
    role : str
        Desirability role: one of ``'target'``, ``'feed'``, ``'side'``,
        ``'undesired'``, ``'inert'`` or ``'water'``.
    fill : str or None, optional
        Hex colour for filled shapes. Defaults to `color`.
    family : str or None, optional
        Name of the scheme hue the colours came from, or ``None`` for a
        literal colour that is not part of the scheme.
    """

    name: str
    color: str
    role: str
    fill: Optional[str] = None
    family: Optional[str] = None

    def __post_init__(self) -> None:
        if self.fill is None:
            object.__setattr__(self, "fill", self.color)


def _from(name: str, hue: ColorFamily, role: str, line: str = "line", fill: str = "base") -> Species:
    """Build a species from a scheme hue, naming its line and fill tones."""
    return Species(
        name=name,
        color=getattr(hue, line),
        role=role,
        fill=getattr(hue, fill),
        family=hue.name,
    )


#: Literal ocean blue for water (H2O reads as blue, so it opts out of the
#: role scheme). Chosen to stay clear of the CO2 blue.
OCEAN = "#0077BE"

#: Deep red for methane, darker than ``RED.line`` so CH4 and the light-red H2
#: stay apart (see the module docstring). A species literal like OCEAN.
METHANE = "#991801"


SPECIES: dict[str, Species] = {
    "MeOH": _from("MeOH", GREEN, "target"),                                  # the target product
    "CO2": _from("CO2", BLUE, "feed", line="darkest", fill="darkest"),       # feed: CO2 the dark blue,
    "H2": _from("H2", RED, "feed", line="light", fill="light"),              #   H2 the light red
    "EtOH": _from("EtOH", PURPLE, "side"),                                   # side products, most
    "MF": _from("MF", PINK, "side"),                                         #   to least desirable:
    "DME": _from("DME", PINK, "side", line="dark", fill="dark"),             #   EtOH -> MF -> DME
    "CH4": Species("CH4", METHANE, "undesired"),                             # undesired: CH4 worst (deep red),
    "CO": _from("CO", AMBER, "undesired"),                                   #   CO amber (also a carbon oxide)
    "H2O": Species("H2O", OCEAN, "water"),                                   # literal ocean blue
    "Ar": _from("Ar", GREY, "inert"),                                        # inert carriers, by lightness
    "He": _from("He", GREY, "inert", line="dark", fill="dark"),
    "N2": _from("N2", GREY, "inert", line="darkest", fill="darkest"),
}

#: Canonical ``{species: hex}`` mapping (backwards-compatible shape): the
#: line colours, which is what a trace or a marker takes.
SPECIES_COLORS: dict[str, str] = {name: s.color for name, s in SPECIES.items()}

#: ``{species: hex}`` of the fill colours, for drawings, bands and patches.
SPECIES_FILL_COLORS: dict[str, str] = {name: s.fill for name, s in SPECIES.items()}

#: ``{species: role}`` mapping, e.g. for muting undesired traces or
#: ordering a legend by desirability.
SPECIES_ROLES: dict[str, str] = {name: s.role for name, s in SPECIES.items()}
