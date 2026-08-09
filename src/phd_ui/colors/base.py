"""
Per-species colours, derived from the PhD colour scheme.

The scheme (:mod:`phd_ui.colors.scheme`) is the shared vocabulary for
schematics and drawings. Species reuse the *same* hues, but here the hue
encodes the species' **role on a desirability axis**, so a plot's colours
also carry meaning rather than just identity:

    ========  ==================  =====================================
    hue       role                species
    ========  ==================  =====================================
    green     target product      MeOH  ("green methanol")
    blue      feed / carbon oxide  CO2, CO, H2
    purple    other product       DME, MF
    warm      undesired byproduct  CH4, EtOH
    grey      inert               Ar, N2
    ========  ==================  =====================================

Water is the one deliberate exception: it takes a literal **ocean blue**
rather than a role colour, because H2O reads as blue. Species within a
role are separated by tone (``base`` / ``dark`` / ``light`` / ``darkest``).

Because the colours are looked up from the scheme, editing a scheme hue
moves every species of that role with it. ``SPECIES_COLORS`` keeps the
historical ``{name: hex}`` shape; ``SPECIES`` and ``SPECIES_ROLES`` expose
the richer structure.
"""

from dataclasses import dataclass
from typing import Optional

from phd_ui.colors.scheme import (
    BLUE,
    GREEN,
    GREY,
    ORANGE,
    PINK,
    PURPLE,
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
        Desirability role: one of ``'target'``, ``'feed'``, ``'other'``,
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
    "CO2": _from("CO2", BLUE, "darkest", "feed"),          # carbon oxide / feed
    "CO": _from("CO", BLUE, "dark", "feed"),
    "H2": _from("H2", BLUE, "base", "feed"),
    "DME": _from("DME", PURPLE, "base", "other"),          # other products
    "MF": _from("MF", PURPLE, "light", "other"),
    "CH4": _from("CH4", PINK, "base", "undesired"),        # undesired byproducts
    "EtOH": _from("EtOH", ORANGE, "base", "undesired"),
    "H2O": Species("H2O", OCEAN, "water", None),           # literal ocean blue
    "Ar": _from("Ar", GREY, "base", "inert"),              # inert carriers
    "N2": _from("N2", GREY, "dark", "inert"),
    "He": _from("He", GREY, "darkest", "inert"),
}

#: Canonical ``{species: hex}`` mapping (backwards-compatible shape).
SPECIES_COLORS: dict[str, str] = {name: s.color for name, s in SPECIES.items()}

#: ``{species: role}`` mapping, e.g. for muting undesired traces or
#: ordering a legend by desirability.
SPECIES_ROLES: dict[str, str] = {name: s.role for name, s in SPECIES.items()}
