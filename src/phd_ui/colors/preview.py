"""
Render the PhD colour scheme as figures.

Seven views, all sized from :func:`phd_ui.plotting.get_figsize` so they
match every other figure in the thesis:

- :func:`plot_swatches`, the tone grid, one row per hue, with hex codes:
  the four fill tones and, set apart, the line tone.
- :func:`plot_ramps`, each hue interpolated into a continuous colormap,
  which is what a sequential map derived from the scheme will look like.
- :func:`plot_demo`, the tones used as they would be in a real plot:
  line tones for the lines, base tones for the fills.
- :func:`plot_species`, the species palette under normal, greyscale and
  deuteranopic vision.
- :func:`plot_nature`, the Nature-branded palette of
  :mod:`phd_ui.colors.nature`, grouped as the artwork guide prints it.
- :func:`plot_wong`, Wong's (2011) colour-blind-safe palette, normal and
  under deuteranopia.
- :func:`plot_atoms`, the atom and bond reference sheet of
  :mod:`phd_ui.colors.atoms`, for placing in Illustrator.

:func:`save_previews` writes them into a directory via
:func:`phd_ui.plotting.save_figure`. The plotting imports happen inside
the functions: :mod:`phd_ui.plotting.params` imports the scheme for its
prop cycle, so this module must not import plotting at import time.
"""

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from phd_ui.colors.manipulation import hex_to_rgb
from phd_ui.colors.nature import NATURE, NATURE_ACCENTS, NATURE_BACKGROUND, NATURE_EXTENDED
from phd_ui.colors.scheme import INK, SCHEME, ColorFamily

__all__ = ["plot_swatches", "plot_ramps", "plot_demo", "plot_species", "plot_nature", "plot_wong",
           "plot_atoms", "save_previews"]

_ROLES = ("light", "base", "dark", "darkest")

#: Column of the line tone in the swatch grid: one empty column after the fills.
_LINE_COL = len(_ROLES) + 0.5

#: Order the species roles read in, most to least desirable-ish.
_SPECIES_ROLE_ORDER = ("target", "feed", "side", "undesired", "water", "inert")

#: Machado (2009) deuteranopia simulation matrix (severity 1.0), applied
#: to linear-light RGB.
_DEUTERANOPIA = np.array([
    [0.367, 0.861, -0.228],
    [0.280, 0.673, 0.047],
    [-0.012, 0.043, 0.969],
])


def _relative_luminance(hex_color: str) -> float:
    """
    WCAG relative luminance of a hex colour.

    Parameters
    ----------
    hex_color : str
        6-digit hex colour code.

    Returns
    -------
    float
        Relative luminance in [0, 1].
    """
    rgb = np.asarray(hex_to_rgb(hex_color, mode="float"))
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return float(np.dot(lin, (0.2126, 0.7152, 0.0722)))


def _label_color(hex_color: str) -> str:
    """
    Pick white or near-black text for legibility on `hex_color`.

    Parameters
    ----------
    hex_color : str
        Background colour the text sits on.

    Returns
    -------
    str
        ``'#ffffff'`` on a dark background, otherwise a near-black.
    """
    return "#ffffff" if _relative_luminance(hex_color) < 0.35 else "#1a1a1a"


def _simulate_deuteranopia(hex_color: str) -> np.ndarray:
    """
    Simulate how a hex colour looks to a deuteranope.

    Parameters
    ----------
    hex_color : str
        6-digit hex colour code.

    Returns
    -------
    numpy.ndarray
        Simulated sRGB triple in [0, 1].
    """
    rgb = np.asarray(hex_to_rgb(hex_color, mode="float"))
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    sim = _DEUTERANOPIA @ lin
    sim = np.clip(sim, 0.0, 1.0)
    srgb = np.where(sim <= 0.0031308, sim * 12.92, 1.055 * sim ** (1 / 2.4) - 0.055)
    return np.clip(srgb, 0.0, 1.0)


def _to_grey(hex_color: str) -> np.ndarray:
    """Perceptual grey (gamma-encoded luminance) of a hex colour."""
    g = _relative_luminance(hex_color) ** (1 / 2.2)
    return np.array([g, g, g])


def plot_species(figsize_key: str = "double") -> Figure:
    """
    The species palette under normal, greyscale and deuteranopic vision.

    Species (from :data:`phd_ui.colors.base.SPECIES`) are grouped by role,
    so the desirability story reads left to right, and shown in three rows:
    normal colour, greyscale (a proxy for black-and-white print) and a
    deuteranopia simulation. It is the check that the palette stays
    distinguishable for colour-blind readers and in mono.

    Parameters
    ----------
    figsize_key : str, optional
        Key into the shared figure-size table. Only used as a lower bound
        on the width; the figure is widened to fit all species if needed.

    Returns
    -------
    Figure
        The finished figure. Not saved, not closed.
    """
    from phd_ui.colors.base import SPECIES
    from phd_ui.plotting.figsize import get_figsize

    species = sorted(
        SPECIES.values(),
        key=lambda s: (_SPECIES_ROLE_ORDER.index(s.role), s.name),
    )
    n = len(species)
    views = (
        ("normal", lambda h: np.asarray(hex_to_rgb(h, mode="float"))),
        ("greyscale", _to_grey),
        ("deuteranopia", _simulate_deuteranopia),
    )

    width = max(get_figsize(figsize_key)[0], 0.62 * n + 1.6)
    fig, ax = plt.subplots(figsize=(width, 0.55 * len(views) + 0.9))

    for row, (label, transform) in enumerate(views):
        y = len(views) - 1 - row
        ax.text(-0.2, y + 0.45, label, ha="right", va="center", fontsize=8, color=INK.base)
        for i, sp in enumerate(species):
            col = np.clip(transform(sp.color), 0.0, 1.0)
            ax.add_patch(Rectangle((i, y), 0.94, 0.9, facecolor=col, edgecolor="none"))
            if row == 0:
                ax.text(i + 0.47, y + 0.45, sp.name, ha="center", va="center",
                        fontsize=7, color=_label_color(sp.color))

    top = len(views) + 0.05
    for role in _SPECIES_ROLE_ORDER:
        members = [i for i, sp in enumerate(species) if sp.role == role]
        if not members:
            continue
        a, b = members[0], members[-1] + 1
        ax.plot([a, b - 0.06], [top, top], color=INK.base, lw=1.5)
        ax.text((a + b) / 2, top + 0.1, role, ha="center", va="bottom",
                fontsize=7, color=INK.base)

    ax.set_xlim(-2.0, n)
    ax.set_ylim(0, len(views) + 0.75)
    ax.set_axis_off()
    return fig


def plot_swatches(figsize_key: str = "single") -> Figure:
    """
    The tone grid: one row per hue, the four fill tones light to dark,
    then the line tone set apart by an empty column.

    A tone a family leaves undefined is drawn blank, so the columns stay
    aligned across hues.

    Parameters
    ----------
    figsize_key : str, optional
        Key into the shared figure-size table. Only the width is taken
        from it; the height scales with the number of hues so the cells
        stay square-ish.

    Returns
    -------
    Figure
        The finished figure. Not saved, not closed.
    """
    from phd_ui.plotting.figsize import get_figsize

    families = list(SCHEME.values())
    width = get_figsize(figsize_key)[0]
    fig, ax = plt.subplots(figsize=(width, 0.62 * len(families) + 0.7))

    columns = [(float(col), role) for col, role in enumerate(_ROLES)] + [(_LINE_COL, "line")]
    for row, family in enumerate(families):
        y = len(families) - 1 - row
        ax.text(-0.15, y + 0.5, family.name, ha="right", va="center",
                fontweight="bold", color=INK.base)
        for col, role in columns:
            color = getattr(family, role)
            if color is None:
                continue
            ax.add_patch(Rectangle((col, y), 0.92, 0.9, facecolor=color,
                                   edgecolor="none"))
            ax.text(col + 0.46, y + 0.45, color, ha="center", va="center",
                    fontsize=6, color=_label_color(color))

    for col, role in columns:
        ax.text(col + 0.46, len(families) + 0.12, role, ha="center",
                va="bottom", fontsize=7, color=INK.base)

    ax.set_xlim(-1.35, _LINE_COL + 1)
    ax.set_ylim(0, len(families) + 0.55)
    ax.set_axis_off()
    return fig


def _family_cmap(family: ColorFamily) -> LinearSegmentedColormap:
    """
    Interpolate a hue's tones into a continuous colormap.

    Parameters
    ----------
    family : ColorFamily
        The hue to build from; its `shades` become the control points.

    Returns
    -------
    LinearSegmentedColormap
        Colormap running light to dark, named after the hue.
    """
    return LinearSegmentedColormap.from_list(family.name, family.shades)


def plot_ramps(figsize_key: str = "single") -> Figure:
    """
    Each hue as a continuous ramp interpolated through its tones.

    This is the preview of what a sequential colormap derived from the
    scheme looks like; hues with only two tones ramp less far.

    Parameters
    ----------
    figsize_key : str, optional
        Key into the shared figure-size table; width only, the height
        scales with the number of hues.

    Returns
    -------
    Figure
        The finished figure.
    """
    from phd_ui.plotting.figsize import get_figsize

    families = list(SCHEME.values())
    width = get_figsize(figsize_key)[0]
    fig, axes = plt.subplots(len(families), 1,
                             figsize=(width, 0.34 * len(families) + 0.5))

    gradient = np.linspace(0, 1, 256)[np.newaxis, :]
    for ax, family in zip(np.atleast_1d(axes), families):
        ax.imshow(gradient, aspect="auto", cmap=_family_cmap(family))
        ax.set_axis_off()
        ax.text(-0.01, 0.5, family.name, transform=ax.transAxes,
                ha="right", va="center", fontsize=7, color=INK.base)

    return fig


def plot_demo(figsize_key: str = "single") -> Figure:
    """
    The tones in use: line tones for the lines, base tones for the fills.

    Shows whether the hues stay distinguishable at the line widths and
    marker sizes the rcParams actually produce, which a swatch grid
    does not.

    Parameters
    ----------
    figsize_key : str, optional
        Key into the shared figure-size table, used in full.

    Returns
    -------
    Figure
        The finished figure.
    """
    from phd_ui.plotting.figsize import get_figsize

    families = list(SCHEME.values())
    fig, (ax_line, ax_bar) = plt.subplots(
        1, 2, figsize=get_figsize(figsize_key)
    )

    x = np.linspace(0, 2 * np.pi, 200)
    for i, family in enumerate(families):
        y = np.sin(x - i * np.pi / len(families))
        ax_line.plot(x, y, color=family.line, label=family.name)
        ax_line.fill_between(x, y, alpha=0.15, color=family.base, lw=0)
    ax_line.set_xlim(x[0], x[-1])
    ax_line.set_xlabel("x")
    ax_line.set_ylabel("y")
    ax_line.legend(fontsize=6, frameon=False, ncols=2)

    heights = np.arange(len(families)) + 1.0
    ax_bar.bar(range(len(families)), heights,
               color=[f.base for f in families],
               edgecolor=[f.dark for f in families])
    ax_bar.set_xticks(range(len(families)))
    ax_bar.set_xticklabels([f.name for f in families], rotation=45,
                           ha="right", fontsize=6)
    ax_bar.set_ylabel("value")

    return fig


def plot_nature(figsize_key: str = "single") -> Figure:
    """
    The Nature-branded palette: one row per family, six steps light to dark.

    Rows are grouped as the artwork guide prints them: the background
    families, the main accents, then the extended palette.

    Parameters
    ----------
    figsize_key : str, optional
        Key into the shared figure-size table; width only, the height
        scales with the number of families.

    Returns
    -------
    Figure
        The finished figure. Not saved, not closed.
    """
    from phd_ui.plotting.figsize import get_figsize

    groups = (
        ("background", NATURE_BACKGROUND),
        ("main accents", NATURE_ACCENTS),
        ("extended", NATURE_EXTENDED),
    )
    rows = [(group, name) for group, names in groups for name in names]
    n_steps = len(next(iter(NATURE.values())))
    width = get_figsize(figsize_key)[0]
    fig, ax = plt.subplots(figsize=(width, 0.5 * len(rows) + 0.9))

    y = len(rows)
    for group, names in groups:
        ax.text(-0.15, y - 0.1, group, ha="right", va="top", fontsize=7,
                fontstyle="italic", color=INK.light)
        for name in names:
            y -= 1
            ax.text(-0.15, y + 0.45, name, ha="right", va="center",
                    fontweight="bold", color=INK.base)
            for col, color in enumerate(NATURE[name]):
                ax.add_patch(Rectangle((col, y), 0.92, 0.9, facecolor=color,
                                       edgecolor="none"))
                ax.text(col + 0.46, y + 0.45, color, ha="center", va="center",
                        fontsize=6, color=_label_color(color))

    for col in range(n_steps):
        ax.text(col + 0.46, len(rows) + 0.12, str(col), ha="center",
                va="bottom", fontsize=7, color=INK.base)

    ax.set_xlim(-1.6, n_steps)
    ax.set_ylim(0, len(rows) + 0.55)
    ax.set_axis_off()
    return fig


def plot_wong(figsize_key: str = "single") -> Figure:
    """
    Wong's (2011) colour-blind-safe palette, normal and as a deuteranope sees it.

    Parameters
    ----------
    figsize_key : str, optional
        Key into the shared figure-size table; width only.

    Returns
    -------
    Figure
        The finished figure. Not saved, not closed.
    """
    from phd_ui.colors.wong import WONG
    from phd_ui.plotting.figsize import get_figsize

    names = list(WONG)
    width = get_figsize(figsize_key)[0]
    fig, ax = plt.subplots(figsize=(width, 1.5))
    rows = (("normal", lambda h: np.asarray(hex_to_rgb(h, mode="float"))),
            ("deuteranopia", _simulate_deuteranopia))
    for row, (label, transform) in enumerate(rows):
        y = len(rows) - 1 - row
        ax.text(-0.15, y + 0.45, label, ha="right", va="center", fontsize=7, color=INK.base)
        for i, name in enumerate(names):
            ax.add_patch(Rectangle((i, y), 0.94, 0.9, facecolor=np.clip(transform(WONG[name]), 0, 1),
                                   edgecolor="none"))
            if row == 0:
                ax.text(i + 0.47, y + 0.45, WONG[name], ha="center", va="center", fontsize=5.5,
                        color=_label_color(WONG[name]))
    for i, name in enumerate(names):
        ax.text(i + 0.47, len(rows) + 0.08, name, ha="center", va="bottom", fontsize=6, color=INK.base)
    ax.set_xlim(-1.9, len(names))
    ax.set_ylim(0, len(rows) + 0.6)
    ax.set_axis_off()
    return fig


def plot_atoms(figsize_key: str = "double") -> Figure:
    """
    The atom and bond reference sheet of :mod:`phd_ui.colors.atoms`.

    Top: every atom at its relative covalent size with its fill, edge and
    light hex codes. Bottom left: the five bond kinds. Bottom right: two
    molecules of the CO2 hydrogenation network drawn ball and stick, and a
    supported particle with an adsorbed formate, the surface conventions in
    use. Meant to be placed in Illustrator and eyedropped from.

    Parameters
    ----------
    figsize_key : str, optional
        Key into the shared figure-size table, used in full.

    Returns
    -------
    Figure
        The finished figure. Not saved, not closed.
    """
    from matplotlib.patches import Wedge

    from phd_ui.colors.atoms import ATOMS, BOND_STYLES, bond_length_pm
    from phd_ui.colors.scheme import SAND
    from phd_ui.plotting.figsize import get_figsize
    from phd_ui.plotting.molecule import draw_atom, draw_bond, draw_molecule

    fig = plt.figure(figsize=get_figsize(figsize_key))
    grid = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.25], width_ratios=[1.0, 3.2])
    ax_atoms = fig.add_subplot(grid[0, :])
    ax_bonds = fig.add_subplot(grid[1, 0])
    ax_mol = fig.add_subplot(grid[1, 1])
    for ax in (ax_atoms, ax_bonds, ax_mol):
        ax.set_aspect("equal")
        ax.set_axis_off()

    # atoms, space-filling so the size comparison is direct
    step = 330.0
    for i, atom in enumerate(ATOMS.values()):
        x = i * step
        draw_atom(ax_atoms, x, 0, atom.symbol, ball_scale=1.0, label=True, fontsize=6.5)
        for j, hexv in enumerate((atom.fill, atom.edge, atom.light)):
            ax_atoms.text(x, -200 - j * 85, hexv, ha="center", va="top", fontsize=5, color=INK.light)
        ax_atoms.text(x, 200, f"{atom.radius_pm:g}", ha="center", va="bottom", fontsize=5, color=INK.light)
    ax_atoms.text(-170, 200, "r / pm", ha="right", va="bottom", fontsize=5, color=INK.light)
    for j, role in enumerate(("fill", "edge", "light")):
        ax_atoms.text(-170, -200 - j * 85, role, ha="right", va="top", fontsize=5, color=INK.light)
    ax_atoms.set_xlim(-420, (len(ATOMS) - 0.5) * step)
    ax_atoms.set_ylim(-470, 330)

    # bond kinds
    for i, kind in enumerate(BOND_STYLES):
        y = -i * 110.0
        draw_bond(ax_bonds, (0, y), (220, y), kind, ends=("C", "O"))
        ax_bonds.text(260, y, kind, va="center", fontsize=6.5, color=INK.base)
    ax_bonds.set_xlim(-20, 620)
    ax_bonds.set_ylim(-500, 80)

    # molecules, ball and stick at true bond lengths
    co = bond_length_pm("C", "O") - 20              # C=O is shorter than the single-bond sum
    ch = bond_length_pm("C", "H")
    oh = bond_length_pm("O", "H")
    draw_molecule(ax_mol, [("O", -co, 0), ("C", 0, 0), ("O", co, 0)], [(0, 1, "double"), (1, 2, "double")])
    ax_mol.text(0, -150, "CO$_2$", ha="center", va="top", fontsize=7, color=INK.base)

    x0 = 560.0
    c_o = bond_length_pm("C", "O")
    meoh = [("C", x0, 0), ("O", x0 + c_o, 0), ("H", x0 + c_o + oh * 0.34, oh * 0.94),
            ("H", x0 - ch * 0.34, ch * 0.94), ("H", x0 - ch * 0.34, -ch * 0.94), ("H", x0 - ch, 0)]
    draw_molecule(ax_mol, meoh, [(0, 1), (1, 2), (0, 3), (0, 4), (0, 5)])
    ax_mol.text(x0 + 70, -150, "CH$_3$OH", ha="center", va="top", fontsize=7, color=INK.base)

    # support, particle with an oxidised rim, GaOx, and a bidentate formate on the particle
    lw = plt.rcParams["lines.linewidth"] / 1.2
    sx, sy, sw = 1050.0, -250.0, 1350.0
    ax_mol.add_patch(Rectangle((sx, sy - 160), sw, 160, facecolor=SAND.base, edgecolor="none", zorder=0))
    ax_mol.plot([sx, sx + sw], [sy, sy], color=SAND.dark, linewidth=0.8 * lw, zorder=0.5)
    ax_mol.text(sx + 30, sy - 80, "SiO$_2$", va="center", fontsize=6.5, color=SAND.darkest)
    cu = ATOMS["Cu"]
    px, pr = sx + 520, 330.0
    ax_mol.add_patch(Wedge((px, sy), pr, 0, 180, facecolor=cu.fill, edgecolor=cu.edge, linewidth=0.6 * lw, zorder=1))
    ax_mol.add_patch(Wedge((px, sy), pr, 0, 35, facecolor=cu.light, edgecolor=cu.edge, linewidth=0.6 * lw,
                           zorder=1.1))
    ax_mol.text(px - 60, sy + 110, "Cu$^0$", ha="center", va="center", fontsize=6.5, color=cu.text, zorder=2)
    for gx, gy in ((px + pr + 90, sy + 85), (px + pr + 260, sy + 85), (px + pr + 175, sy + 230)):
        draw_atom(ax_mol, gx, gy, "Ga", ball_scale=0.7)
    ax_mol.text(px + pr + 175, sy + 400, "GaO$_x$", ha="center", fontsize=6.5, color=INK.base)
    fx, fy = px + 150, sy + pr + 180
    o1, o2 = (fx - 110, fy - 60), (fx + 110, fy - 60)
    draw_molecule(ax_mol, [("C", fx, fy), ("O", *o1), ("O", *o2), ("H", fx, fy + ch)],
                  [(0, 1, "partial"), (0, 2, "partial"), (0, 3)])
    for o in (o1, o2):
        draw_bond(ax_mol, o, (o[0], o[1] - 150), "surface")
    ax_mol.text(fx + 210, fy + 60, "HCOO*", va="center", fontsize=6.5, color=INK.base)
    ax_mol.set_xlim(-260, sx + sw + 20)
    ax_mol.set_ylim(sy - 180, 560)
    return fig


def save_previews(figure_path: str | Path,
                  figsize_key: str = "single",
                  prefix: str = "colorscheme",
                  close: bool = True) -> dict[str, Figure]:
    """
    Render the scheme previews and write them to `figure_path`.

    Parameters
    ----------
    figure_path : str or Path
        Existing directory to write into. Each figure is written as
        png, pdf and svg by :func:`phd_ui.plotting.save_figure`.
    figsize_key : str, optional
        Key into the shared figure-size table, passed to each plot.
    prefix : str, optional
        Filename prefix; the views are suffixed ``_swatches``,
        ``_ramps``, ``_demo``, ``_nature``, ``_wong`` and ``_atoms``.
    close : bool, optional
        If True (default), close the figures after saving. Set False to
        keep them for display in a notebook.

    Returns
    -------
    dict[str, Figure]
        The figures, keyed by view name.

    Raises
    ------
    FileNotFoundError
        If `figure_path` does not exist.
    """
    from phd_ui.plotting.export import save_figure

    directory = Path(figure_path)
    if not directory.is_dir():
        raise FileNotFoundError(f"Not a directory: {directory}")

    figures: dict[str, Figure] = {
        "swatches": plot_swatches(figsize_key),
        "ramps": plot_ramps(figsize_key),
        "demo": plot_demo(figsize_key),
        "nature": plot_nature(figsize_key),
        "wong": plot_wong(figsize_key),
        "atoms": plot_atoms("double"),
    }
    for view, fig in figures.items():
        save_figure(fig, directory, f"{prefix}_{view}")
        if close:
            plt.close(fig)
    return figures
