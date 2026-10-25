"""
Draw atoms and bonds by the conventions of :mod:`phd_ui.colors.atoms`.

Coordinates are data coordinates on an axes with an equal aspect ratio, in
pm: place atoms at their real positions and the drawing comes out with true
bond lengths. Atom sizes are the compressed radii of the atom convention
(``Atom.drawn_pm``), so size differences are indicated, not to scale. Bonds go under the atoms (lower
zorder), so they need no trimming at the atom edge.

Line widths follow the active preset: the style widths are print widths and
are multiplied by the preset's scale, read off ``lines.linewidth`` (1.2 pt
in print, 2.4 pt on a slide), so a molecule drawn under a slide preset gets
the same 2x as everything else.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon

from phd_ui.colors.atoms import ATOMS, BALL_SCALE, BOND_STYLES, get_atom

__all__ = ["draw_atom", "draw_bond", "draw_molecule", "draw_projection", "save_spin_gif"]

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
        Drawn radius as a fraction of the compressed covalent radius
        (``Atom.drawn_pm``). ``BALL_SCALE`` (0.38, default) is ball and stick; 1.0 is
        space-filling.
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
    disc = Circle((x, y), atom.drawn_pm * ball_scale, facecolor=atom.fill, edgecolor=atom.edge,
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
        gap = min(get_atom(e).drawn_pm for e in ends) * ball_scale / 3
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
    order: list[int] | None = None,
    scale: list[float] | None = None,
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
    order : list of int, optional
        Atom indices in drawing order, back to front, so a nearer atom
        covers a farther one. ``phd_ui.structure.project`` returns it as
        ``Projection.order``; by default the list order.
    scale : list of float, optional
        Radius factor per atom, ``Projection.scale`` (depth cue and
        perspective); by default 1 for every atom.

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
    for n, i in enumerate(order if order is not None else range(len(atoms))):
        symbol, x, y = atoms[i]
        f = 1.0 if scale is None else float(scale[i])
        draw_atom(ax, x, y, symbol, ball_scale=ball_scale * f, label=label, zorder=_ATOM_Z + n * 1e-3)


def draw_projection(ax: plt.Axes, projection: object, *, x: float = 0.0, y: float = 0.0,
                    look: object = None) -> object:
    """
    Draw a ``phd_ui.structure`` projection with matplotlib, as ``sketch.molecule`` does in SVG.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes, equal aspect, **limits already set**: widths in pt are
        converted to data units with the current x limits.
    projection : phd_ui.structure.Projection
        From ``structure.project``, ``skeletal`` or ``spin``.
    x, y : float, optional
        Position of the projection's origin, pm (y up, as in the data).
    look : phd_ui.structure.Look, optional
        Appearance of every atom and bond; default ``Look()``.

    Returns
    -------
    phd_ui.structure.Drawing
        What was drawn, with atom positions and radii.
    """
    from phd_ui.structure import render

    k = _scale()
    x0, x1 = ax.get_xlim()
    width_pt = ax.get_position().width * ax.figure.get_figwidth() * 72
    drawing = render(projection, look, pm_per_pt=(x1 - x0) / width_pt * k if width_pt else 1.0)
    for z, it in enumerate(drawing.items):
        zo = 3.0 + z * 1e-3
        if it.type == "circle":
            ax.add_patch(Circle((x + it.cx, y + it.cy), it.r, facecolor=it.fill, edgecolor=it.stroke,
                                linewidth=it.stroke_width_pt * k, alpha=it.opacity, zorder=zo,
                                linestyle=(0, [v / it.stroke_width_pt for v in it.dash_pt]) if it.dash_pt else "solid"))
        elif it.type == "line":
            ls = (0, [v / it.width_pt for v in it.dash_pt]) if it.dash_pt else "solid"
            ax.plot([x + it.x0, x + it.x1], [y + it.y0, y + it.y1], color=it.color, linewidth=it.width_pt * k,
                    linestyle=ls, solid_capstyle=it.cap, dash_capstyle=it.cap, alpha=it.opacity, zorder=zo)
        else:
            ax.add_patch(Polygon([(x + px, y + py) for px, py in it.points], closed=True, facecolor=it.fill,
                                 edgecolor="none", alpha=it.opacity, zorder=zo))
    return drawing


def save_spin_gif(frames: list, path: str, *, period_s: float = 6.0, size_cm: tuple[float, float] = (4.0, 4.5),
                  dpi: int = 150, look: object = None) -> str:
    """
    Write a turning molecule as an animated GIF, with matplotlib only.

    Parameters
    ----------
    frames : list of phd_ui.structure.Projection
        From ``structure.spin``.
    path : str or pathlib.Path
        Output ``.gif``.
    period_s : float, optional
        Seconds per full turn.
    size_cm : tuple of float, optional
        Image size, cm.
    dpi : int, optional
        Resolution.
    look : phd_ui.structure.Look, optional
        Appearance.

    Returns
    -------
    str
        The path written.

    Notes
    -----
    matplotlib's ``PillowWriter`` (Pillow ships with matplotlib), so it runs
    wherever ``phd_ui`` does. Frames are opaque white with fixed limits
    over the whole turn, so nothing jumps or piles up.
    """
    from matplotlib.animation import FuncAnimation, PillowWriter

    from phd_ui.structure import render

    boxes = np.array([render(f, look).bounds() for f in frames])
    lo, hi = boxes[:, :2].min(axis=0), boxes[:, 2:].max(axis=0)
    centre, half = (lo + hi) / 2, (hi - lo) / 2 * 1.08
    ratio = size_cm[0] / size_cm[1]
    half = np.array([max(half[0], half[1] * ratio), max(half[1], half[0] / ratio)])
    rc = {"figure.constrained_layout.use": False, "savefig.bbox": None, "savefig.transparent": False,
          "savefig.facecolor": "white", "figure.facecolor": "white"}
    with plt.rc_context(rc):
        fig = plt.figure(figsize=(size_cm[0] / 2.54, size_cm[1] / 2.54))
        ax = fig.add_axes((0, 0, 1, 1))

        def frame(n: int) -> list:
            ax.clear()
            ax.set_xlim(centre[0] - half[0], centre[0] + half[0])
            ax.set_ylim(centre[1] - half[1], centre[1] + half[1])
            ax.set_aspect("equal")
            ax.axis("off")
            draw_projection(ax, frames[n], look=look)
            return []

        FuncAnimation(fig, frame, frames=len(frames)).save(str(path), writer=PillowWriter(fps=len(frames) / period_s),
                                                          dpi=dpi)
    plt.close(fig)
    return str(path)
