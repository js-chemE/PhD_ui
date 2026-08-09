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
    blue          feed            CO2, H2
    purple/pink   side product    EtOH (purple), MF, DME (pink)
    red / amber   undesired       CH4 (red, worst), CO (amber)
    ocean         water           H2O
    grey          inert           Ar, He, N2
    ============  ==============  =====================================

This is a desirability gradient: cool = wanted, warm = not. The side
products run from EtOH (purple, nearest the green target, being a valuable
alcohol like methanol) through MF to DME (pink, nearest the undesired end).
The two undesired species get their own warm hues -- CH4 the vivid red as
the worst, CO an amber -- which keeps the scheme's **orange free as a
general marking / annotation colour**. Water is the one deliberate
exception: a literal **ocean blue**, because H2O reads as blue. Species
within a role are separated by tone (``base`` / ``dark`` / ``light`` /
``darkest``).

Because the colours are looked up from the scheme, editing a scheme hue
moves every species of that role with it. ``SPECIES_COLORS`` keeps the
historical ``{name: hex}`` shape; ``SPECIES`` and ``SPECIES_ROLES`` expose
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

__all__ = ["Species", "SPECIES", "SPECIES_COLORS", "SPECIES_ROLES"]


@dataclass(frozen=True)
class Species:
    """
    One chemical species and the colour it is drawn in.

    Parameters
    ----------
    name : str
        Species abbreviation, e.g. ``'MeOH'``.
    color : str
        Hex colour, resolved from the scheme (or a literal for water).
    role : str
        Desirability role: one of ``'target'``, ``'feed'``, ``'side'``,
        ``'undesired'``, ``'inert'`` or ``'water'``.
    family : str or None
        Name of the scheme hue the colour came from, or ``None`` for a
        literal colour that is not part of the scheme.
    """

    name: str
    color: str
    role: str
    family: Optional[str] = None


def _from(name: str, hue: ColorFamily, tone: str, role: str) -> Species:
    """Build a species from a scheme hue and one of its tones."""
    return Species(name=name, color=getattr(hue, tone), role=role, family=hue.name)


#: Literal ocean blue for water (H2O reads as blue, so it opts out of the
#: role scheme). Chosen to stay clear of the feed blues.
OCEAN = "#0077BE"


SPECIES: dict[str, Species] = {
    "MeOH": _from("MeOH", GREEN, "base", "target"),        # the target product
    "CO2": _from("CO2", BLUE, "darkest", "feed"),          # feed
    "H2": _from("H2", BLUE, "base", "feed"),
    "EtOH": _from("EtOH", PURPLE, "base", "side"),         # side products, most
    "MF": _from("MF", PINK, "base", "side"),               #   to least desirable:
    "DME": _from("DME", PINK, "dark", "side"),             #   EtOH -> MF -> DME
    "CH4": _from("CH4", RED, "base", "undesired"),         # undesired: CH4 worst (red),
    "CO": _from("CO", AMBER, "base", "undesired"),         #   CO amber (also a carbon oxide)
    "H2O": Species("H2O", OCEAN, "water", None),           # literal ocean blue
    "Ar": _from("Ar", GREY, "base", "inert"),              # inert carriers
    "He": _from("He", GREY, "dark", "inert"),
    "N2": _from("N2", GREY, "darkest", "inert"),
}

#: Canonical ``{species: hex}`` mapping (backwards-compatible shape).
SPECIES_COLORS: dict[str, str] = {name: s.color for name, s in SPECIES.items()}

#: ``{species: role}`` mapping, e.g. for muting undesired traces or
#: ordering a legend by desirability.
SPECIES_ROLES: dict[str, str] = {name: s.role for name, s in SPECIES.items()}
