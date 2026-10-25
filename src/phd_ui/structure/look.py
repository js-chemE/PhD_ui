"""
How a molecule looks: every property of every atom and bond, overridable.

A :class:`Look` holds the defaults of the atom convention
(:mod:`phd_ui.colors.atoms`) and lets any of them be changed per element,
per bond kind, per single atom (by label, ``'O2'``) or per single bond
(``'C1-O2'``). Nothing is fixed in the renderers; they draw what the look
resolves to.

Resolution, most specific last wins::

    atom:  ATOMS[symbol] defaults -> Look.elements[symbol] -> Look.atoms[label]
    bond:  BOND_STYLES[kind]      -> Look.kinds[kind]      -> Look.bonds["C1-O2"]

Examples
--------
>>> look = Look(depth_cue=0.3, elements={"H": AtomLook(opacity=0.6)},
...             atoms={"O2": AtomLook(fill="#2b73b8", radius_factor=1.2)},
...             bonds={"C1-O2": BondLook(color="#c44036", width_pt=2.0)})
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, replace

from phd_ui.colors.atoms import BALL_SCALE, BOND_STYLES, SIZE_EXPONENT, drawn_radius_pm, get_atom, get_ion

__all__ = ["AtomLook", "BondLook", "DEPTH_CUE", "Look"]

#: Default size cue from depth: an atom at the molecule's full reach pointing
#: at the viewer is drawn this fraction larger, pointing away this much smaller.
DEPTH_CUE: float = 0.2


@dataclass(frozen=True)
class AtomLook:
    """
    Appearance of one atom. ``None`` keeps the value from the level below.

    Attributes
    ----------
    fill, edge : str
        Colours.
    edge_width_pt : float
        Outline width, pt at print scale.
    edge_dash_pt : tuple of float
        Outline dash pattern in pt; ``()`` for solid.
    opacity : float
        0 to 1, for the whole atom.
    radius_pm : float
        True radius to start from (covalent by default); set an ionic one
        here, or any value.
    radius_factor : float
        Multiplier on the drawn radius after everything else.
    """

    fill: str | None = None
    edge: str | None = None
    edge_width_pt: float | None = None
    edge_dash_pt: tuple[float, ...] | None = None
    opacity: float | None = None
    radius_pm: float | None = None
    radius_factor: float | None = None


@dataclass(frozen=True)
class BondLook:
    """
    Appearance of one bond. ``None`` keeps the value from the level below.

    Attributes
    ----------
    color : str
        Line (or wedge) colour.
    width_pt : float
        Width of each line, pt at print scale.
    lines : int
        Parallel lines (2 double, 3 triple).
    spacing_pt : float
        Centre distance of parallel lines, pt.
    dash_pt : tuple of float
        Dash pattern in pt; ``()`` solid.
    opacity : float
        0 to 1.
    cap : str
        ``'butt'`` or ``'round'``.
    """

    color: str | None = None
    width_pt: float | None = None
    lines: int | None = None
    spacing_pt: float | None = None
    dash_pt: tuple[float, ...] | None = None
    opacity: float | None = None
    cap: str | None = None


def _merge(base, *overrides):
    """Fields of each override that are not None replace those of `base`."""
    for o in overrides:
        if o is not None:
            base = replace(base, **{f.name: v for f in fields(o) if (v := getattr(o, f.name)) is not None})
    return base


def _kind_default(kind: str) -> BondLook:
    s = BOND_STYLES[kind]
    dash = tuple(v * s.width_pt for v in s.linestyle[1]) if isinstance(s.linestyle, tuple) else ()
    return BondLook(s.color, s.width_pt, s.lines, s.spacing_pt, dash, 1.0, "butt")


@dataclass(frozen=True)
class Look:
    """
    Appearance of a whole molecule drawing.

    Attributes
    ----------
    ball_scale : float
        Drawn radius as a fraction of the (compressed) radius; 1 is
        space-filling.
    size_exponent : float
        Size compression of the atom convention; 1 draws true radii.
    depth_cue : float
        Size cue from depth (radii only): ``1 + depth_cue * depth / reach``.
    ions : tuple of str
        Ions whose elements take their ionic radius (``('Ga3+', 'O2-')``).
    elements : dict of str to AtomLook
        Overrides per element symbol.
    atoms : dict of str to AtomLook
        Overrides per atom label (``'O2'``).
    kinds : dict of str to BondLook
        Overrides per bond kind (``'single'``, ``'double'``, ...).
    bonds : dict of str to BondLook
        Overrides per bond, keyed ``'C1-O2'`` (either order).
    stereo_width_pt : float
        Width of a wedge or hash at its wide end, pt.
    hash_step_pt : float
        Distance between the strokes of a hash, pt.
    trim : bool
        End sticks at the far ball's surface in 3D (True), or run every
        stick centre to centre under both balls (False, flat style).
    """

    ball_scale: float = BALL_SCALE
    size_exponent: float = SIZE_EXPONENT
    depth_cue: float = DEPTH_CUE
    ions: tuple[str, ...] = ()
    elements: dict[str, AtomLook] = field(default_factory=dict)
    atoms: dict[str, AtomLook] = field(default_factory=dict)
    kinds: dict[str, BondLook] = field(default_factory=dict)
    bonds: dict[str, BondLook] = field(default_factory=dict)
    stereo_width_pt: float = 5.0
    hash_step_pt: float = 1.7
    trim: bool = True

    def atom(self, symbol: str, label: str) -> AtomLook:
        """The resolved look of one atom, every field set."""
        a = get_atom(symbol)
        ion = {get_ion(k).symbol: get_ion(k).radius_pm for k in self.ions}.get(symbol)
        base = AtomLook(a.fill, a.edge, 0.6, (), 1.0, ion if ion is not None else a.radius_pm, 1.0)
        return _merge(base, self.elements.get(symbol), self.atoms.get(label))

    def radius(self, symbol: str, label: str, factor: float = 1.0) -> float:
        """Drawn radius in pm: compressed true radius x ball_scale x radius_factor x `factor`."""
        a = self.atom(symbol, label)
        return drawn_radius_pm(a.radius_pm, self.size_exponent) * self.ball_scale * a.radius_factor * factor

    def bond(self, kind: str, a: str, b: str) -> BondLook:
        """The resolved look of one bond between atoms labelled `a` and `b`."""
        own = self.bonds.get(f"{a}-{b}") or self.bonds.get(f"{b}-{a}")
        base = _kind_default(kind) if kind in BOND_STYLES else _kind_default("single")
        return _merge(base, self.kinds.get(kind), own)
