"""
Atom and bond conventions for molecule and surface drawings.

One reference for every place an atom is drawn: the IR-bands animations,
matplotlib schematics, and drawings finished in Illustrator. The rules are
deliberately few, so a figure built by hand matches one built in code.

Atoms
-----
- **Colour is CPK**, the convention every chemist decodes without a key:
  H white, C dark grey, N blue, O red, P orange, S yellow. The hues are
  CPK/Jmol; the tones are pulled to the chroma of the PhD scheme so atoms
  sit beside the rest of a drawing instead of shouting over it. Where the
  scheme has the hue, the scheme tone is used outright (O is ``RED.line``,
  P is ``ORANGE.line``, C is ``GREY.darkest``, the generic metal M is
  ``GREY.base``, H is ``SAND.light``).
- **Carbon is a dark grey, not black.** Black reads as a hole in a flat
  drawing and swallows the bonds drawn into it; ``GREY.darkest`` keeps C
  the darkest atom while the ink-coloured bonds stay visible against it.
- **Flat.** One fill, one thin edge in a darker tone of the same hue, no
  gradient, no highlight, no shadow. Hansen et al. (2025) draw this way and
  it survives reduction to a 9 cm column; shading does not.
- **Size is the covalent radius** (Cordero et al., Dalton Trans. 2008,
  2832), scaled by one factor per figure. H is drawn at that true size and
  so comes out small, which is right: it is the atom readers least need.

Bonds
-----
Bonds are drawn first and the atoms on top, so a bond needs no trimming.
Its *visible* length is then the centre distance minus both drawn radii.
With radii at ``BALL_SCALE`` (0.5) of the covalent radius and centres at
the true bond length (the sum of the covalent radii), the visible stick is
about half the centre distance: long enough to show a double bond's two
lines, short enough that the molecule still reads as one object. At a
``BALL_SCALE`` of 1.0 the atoms touch and the drawing becomes
space-filling, which is the right choice for a nanoparticle or a slab.

``BOND_STYLES`` holds the five kinds, all in the light ink tone:

==========  ==========================================================
single      one line
double      two thinner parallel lines
triple      three thinner parallel lines
partial     dashed, for a delocalised or partial bond (formate O-C-O)
surface     dotted and grey, for the bond of an adsorbate to a surface
==========  ==========================================================

Surfaces and particles, as a convention for drawings: a support is a slab
in ``SAND.base`` with a ``SAND.dark`` top edge and its formula written on
it; a particle is a hemisphere in the metal's colour; an oxidised rim or
an interface phase is a lighter tint of that metal (``ATOMS[x].light``),
not red, so red stays oxygen and lightness carries oxidation state, as it
carries progress elsewhere in the scheme.

Labels
------
Write the symbol inside an atom only when the atom is large enough to hold
it, at least about 4 mm across at final size (a 6 pt capital is 2.1 mm
tall and needs room around it), and never inside H. In a print figure at
9 or 18 cm most atoms are smaller than that, so the colour carries the
element and the first instance is labelled outside the atom, or a key
names the colours once. ``Atom.text`` is the colour a symbol takes when it
is written inside.
"""

from dataclasses import dataclass

from phd_ui.colors.scheme import GREY, INK, ORANGE, RED, SAND

__all__ = [
    "Atom",
    "ATOMS",
    "BALL_SCALE",
    "BondStyle",
    "BOND_STYLES",
    "BOND_COLOR",
    "LABEL_MIN_DIAMETER_MM",
    "bond_length_pm",
    "get_atom",
]

#: Drawn radius as a fraction of the covalent radius, for ball and stick.
BALL_SCALE: float = 0.5

#: Smallest drawn atom diameter, in mm at final size, that holds a symbol.
LABEL_MIN_DIAMETER_MM: float = 4.0

#: Colour of every bond line: the light ink, softer than the darkest atom.
BOND_COLOR: str = INK.light


@dataclass(frozen=True)
class Atom:
    """
    How one element is drawn.

    Parameters
    ----------
    symbol : str
        Element symbol, or ``'M'`` for a generic metal.
    name : str
        Element name, lowercase.
    fill : str
        Hex colour of the disc.
    edge : str
        Hex colour of its outline, a darker tone of `fill`.
    light : str
        A lighter tint of `fill`, for an oxidised rim or an interface phase
        drawn in the same element's colour: `fill` lifted by 0.16 in OKLCH
        lightness at 0.55 of its chroma (a scheme tone where the element
        takes its fill from the scheme).
    text : str
        Hex colour of a symbol written inside the disc.
    radius_pm : float
        Single-bond covalent radius, in pm.
    """

    symbol: str
    name: str
    fill: str
    edge: str
    light: str
    text: str
    radius_pm: float


_WHITE_TEXT = "#ffffff"
_DARK_TEXT = INK.base

ATOMS: dict[str, Atom] = {a.symbol: a for a in (
    #    symbol name          fill          edge       light      text         r / pm
    Atom("H", "hydrogen",   SAND.light,   "#a7a195", "#ffffff", _DARK_TEXT,  31),
    Atom("C", "carbon",     GREY.darkest, "#2b2d30", GREY.dark, _WHITE_TEXT, 76),
    Atom("N", "nitrogen",   "#4160c4",    "#13246d", "#8197d0", _WHITE_TEXT, 71),
    Atom("O", "oxygen",     RED.line,     "#7a1f1a", RED.light, _WHITE_TEXT, 66),
    Atom("P", "phosphorus", ORANGE.line,  "#7b2800", ORANGE.light, _WHITE_TEXT, 107),
    Atom("S", "sulfur",     "#d8d958",    "#91922e", "#f2f4b4", _DARK_TEXT,  105),
    Atom("Al", "aluminium", "#bd9b9b",    "#755c5c", "#e6d2d2", _DARK_TEXT,  121),
    Atom("Si", "silicon",   "#d9b795",    "#8e755c", "#feebd8", _DARK_TEXT,  111),
    Atom("Ni", "nickel",    "#6ca26a",    "#365e34", "#b0ceae", _WHITE_TEXT, 124),
    Atom("Cu", "copper",    "#bb731e",    "#683b02", "#d8ae88", _WHITE_TEXT, 132),
    Atom("Zn", "zinc",      "#797caa",    "#3d3f60", "#adafca", _WHITE_TEXT, 122),
    Atom("Ga", "gallium",   "#be7e7f",    "#724445", "#dfb9b9", _DARK_TEXT,  122),
    Atom("Pd", "palladium", "#2b738b",    "#013343", "#7c9fad", _WHITE_TEXT, 139),
    Atom("In", "indium",    "#a06a68",    "#573130", "#c2a2a0", _WHITE_TEXT, 142),
    Atom("Pt", "platinum",  "#a9a9ba",    "#686774", "#dddde7", _DARK_TEXT,  136),
    Atom("M", "metal",      GREY.base,    GREY.dark, GREY.light, _DARK_TEXT, 135),
)}


@dataclass(frozen=True)
class BondStyle:
    """
    How one kind of bond is drawn.

    Parameters
    ----------
    kind : str
        ``'single'``, ``'double'``, ``'triple'``, ``'partial'`` or
        ``'surface'``.
    lines : int
        Number of parallel lines.
    width_pt : float
        Width of each line, in pt at print scale.
    spacing_pt : float
        Centre-to-centre gap between parallel lines, in pt.
    linestyle : str or tuple
        Matplotlib dash pattern.
    color : str
        Line colour.
    """

    kind: str
    lines: int
    width_pt: float
    spacing_pt: float
    linestyle: str | tuple
    color: str


BOND_STYLES: dict[str, BondStyle] = {s.kind: s for s in (
    BondStyle("single", 1, 1.4, 0.0, "solid", BOND_COLOR),
    BondStyle("double", 2, 0.9, 2.0, "solid", BOND_COLOR),
    BondStyle("triple", 3, 0.8, 1.8, "solid", BOND_COLOR),
    BondStyle("partial", 1, 1.4, 0.0, (0, (3, 2)), BOND_COLOR),
    BondStyle("surface", 1, 1.1, 0.0, (0, (1, 2)), GREY.dark),
)}


def get_atom(symbol: str) -> Atom:
    """
    Look up how an element is drawn.

    Parameters
    ----------
    symbol : str
        Element symbol, case-sensitive as written (``'Cu'``, not ``'CU'``).

    Returns
    -------
    Atom
        The drawing convention for that element.

    Raises
    ------
    KeyError
        If the element has no entry; the message lists the known symbols
        and points at ``'M'`` for a metal without one.
    """
    if symbol not in ATOMS:
        raise KeyError(f"No drawing convention for '{symbol}'. Known: {', '.join(ATOMS)}; "
                       "use 'M' for a metal without its own entry.")
    return ATOMS[symbol]


def bond_length_pm(a: str, b: str) -> float:
    """
    Centre distance of two bonded atoms: the sum of their covalent radii.

    Parameters
    ----------
    a, b : str
        Element symbols.

    Returns
    -------
    float
        Bond length in pm, accurate to about 5 % for single bonds.

    Notes
    -----
    Use it for the centre distance in a drawing and scale the drawn radii by
    :data:`BALL_SCALE`; the visible bond is then about half the distance.
    """
    return get_atom(a).radius_pm + get_atom(b).radius_pm
