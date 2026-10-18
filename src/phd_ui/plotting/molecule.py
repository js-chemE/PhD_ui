"""
Draw atoms and bonds by the conventions of :mod:`phd_ui.colors.atoms`.

Coordinates are data coordinates on an axes with an equal aspect ratio, in
pm: place atoms at their real positions and the drawing comes out with true
bond lengths and true relative sizes. Bonds go under the atoms (lower
zorder), so they need no trimming at the atom edge.

Line widths follow the active preset: the style widths are print widths and
are multiplied by the preset's scale, read off ``lines.linewidth`` (1.2 pt
in print, 2.4 pt on a slide), so a molecule drawn under a slide preset gets
the same 2x as everything else.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

from phd_ui.colors.atoms import ATOMS, BALL_SCALE, BOND_STYLES, get_atom

__all__ = ["draw_atom", "draw_bond", "draw_molecule"]

_PRINT_LINEWIDTH = 1.2
_ATOM_Z = 3.0
_BOND_Z = 2.0


def _scale() -> float:
    """Preset scale, read off the active line width."""
    return plt.rcParams["lines.linewidth"] / _PRINT_LINEWIDTH


def draw_atom(
    ax: plt.Axes,
    x: float,
    y: float,
    symbol: str,
    *,
    ball_scale: float = BALL_SCALE,
    label: bool = False,
    fontsize: float | None = None,
    zorder: float = _ATOM_Z,
) -> Circle:
    """
    Draw one atom as a flat disc.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes, with an equal aspect ratio for round atoms.
    x, y : float
        Centre, in pm.
    symbol : str
        Element symbol, a key of :data:`phd_ui.colors.ATOMS`.
    ball_scale : float, optional
        Drawn radius as a fraction of the covalent radius. 0.5 (default) is
        ball and stick; 1.0 is space-filling.
    label : bool, optional
        If True, write the symbol inside. Only worth it for atoms of at
        least ``LABEL_MIN_DIAMETER_MM`` at final size; never done for H.
    fontsize : float, optional
        Font size of the symbol. Default is the preset's tick size.
    zorder : float, optional
        Drawing order; the default sits above bonds.

    Returns
    -------
    matplotlib.patches.Circle
        The disc.
    """
    atom = get_atom(symbol)
    disc = Circle((x, y), atom.radius_pm * ball_scale, facecolor=atom.fill, edgecolor=atom.edge,
                  linewidth=0.6 * _scale(), zorder=zorder)
    ax.add_patch(disc)
    if label and symbol != "H":
        ax.text(x, y, symbol, ha="center", va="center", color=atom.text, zorder=zorder + 0.1,
                fontsize=fontsize if fontsize is not None else plt.rcParams["xtick.labelsize"])
    return disc


def draw_bond(
    ax: plt.Axes,
    p0: tuple[float, float],
    p1: tuple[float, float],
    kind: str = "single",
    *,
    ends: tuple[str, str] | None = None,
    ball_scale: float = BALL_SCALE,
    zorder: float = _BOND_Z,
) -> list[plt.Line2D]:
    """
    Draw one bond between two atom centres.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes.
    p0, p1 : tuple of float
        The two centres, in pm.
    kind : str, optional
        A key of :data:`phd_ui.colors.BOND_STYLES`: ``'single'``,
        ``'double'``, ``'triple'``, ``'partial'`` or ``'surface'``.
    ends : tuple of str, optional
        Symbols of the two atoms. Sets the gap between parallel lines to a
        third of the smaller drawn radius; without it the gap is 12 pm.
    ball_scale : float, optional
        As in :func:`draw_atom`, for the gap computation.
    zorder : float, optional
        Drawing order; the default sits under the atoms.

    Returns
    -------
    list of matplotlib.lines.Line2D
        One line per parallel stroke.

    Raises
    ------
    KeyError
        If `kind` is not a known bond style.
    """
    if kind not in BOND_STYLES:
        raise KeyError(f"Unknown bond kind '{kind}'. Available: {', '.join(BOND_STYLES)}")
    style = BOND_STYLES[kind]
    a, b = np.asarray(p0, dtype=float), np.asarray(p1, dtype=float)
    d = b - a
    normal = np.array([-d[1], d[0]]) / max(np.hypot(*d), 1e-12)
    if ends is not None:
        gap = min(get_atom(e).radius_pm for e in ends) * ball_scale / 3
    else:
        gap = 12.0
    offsets = (np.arange(style.lines) - (style.lines - 1) / 2) * gap
    lines = []
    for off in offsets:
        s, e = a + off * normal, b + off * normal
        (line,) = ax.plot([s[0], e[0]], [s[1], e[1]], color=style.color, linewidth=style.width_pt * _scale(),
                          linestyle=style.linestyle, solid_capstyle="butt", zorder=zorder)
        lines.append(line)
    return lines


def draw_molecule(
    ax: plt.Axes,
    atoms: list[tuple[str, float, float]],
    bonds: list[tuple[int, int] | tuple[int, int, str]],
    *,
    ball_scale: float = BALL_SCALE,
    label: bool = False,
) -> None:
    """
    Draw a whole molecule: bonds first, atoms on top.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes, with an equal aspect ratio.
    atoms : list of (str, float, float)
        ``(symbol, x, y)`` per atom, positions in pm.
    bonds : list of tuple
        ``(i, j)`` or ``(i, j, kind)`` indices into `atoms`; kind defaults
        to ``'single'``.
    ball_scale : float, optional
        As in :func:`draw_atom`.
    label : bool, optional
        Write the symbols inside the atoms, H excepted.

    Examples
    --------
    >>> from phd_ui.colors import bond_length_pm
    >>> d = bond_length_pm("C", "O") - 10        # a C=O is shorter than a C-O
    >>> draw_molecule(ax, [("O", -d, 0), ("C", 0, 0), ("O", d, 0)],
    ...               [(0, 1, "double"), (1, 2, "double")])
    """
    for bond in bonds:
        i, j = bond[0], bond[1]
        kind = bond[2] if len(bond) > 2 else "single"
        draw_bond(ax, atoms[i][1:], atoms[j][1:], kind, ends=(atoms[i][0], atoms[j][0]), ball_scale=ball_scale)
    for symbol, x, y in atoms:
        draw_atom(ax, x, y, symbol, ball_scale=ball_scale, label=label)
