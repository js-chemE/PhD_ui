"""
Render the PhD colour scheme as figures.

Three views, all sized from :func:`phd_ui.plotting.get_figsize` so they
match every other figure in the thesis:

- :func:`plot_swatches`, the tone grid, one row per hue, with hex codes.
- :func:`plot_ramps`, each hue interpolated into a continuous colormap,
  which is what a sequential map derived from the scheme will look like.
- :func:`plot_demo`, the base tones used as they would be in a real
  plot: lines, filled patches and markers.

:func:`save_previews` writes all three into a directory via
:func:`phd_ui.plotting.save_figure`.
"""

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from phd_ui.colors.manipulation import hex_to_rgb
from phd_ui.colors.scheme import INK, SCHEME, ColorFamily
from phd_ui.plotting.export import save_figure
from phd_ui.plotting.figsize import get_figsize

__all__ = ["plot_swatches", "plot_ramps", "plot_demo", "plot_species", "save_previews"]

_ROLES = ("light", "base", "dark", "darkest")

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
    fig.tight_layout()
    return fig


def plot_swatches(figsize_key: str = "single") -> Figure:
    """
    The tone grid: one row per hue, one cell per tone, light to dark.

    Undefined tones (`pink` and `orange` have no `light` or `darkest`)
    are left blank, so the columns stay aligned across hues.

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
    families = list(SCHEME.values())
    width = get_figsize(figsize_key)[0]
    fig, ax = plt.subplots(figsize=(width, 0.62 * len(families) + 0.7))

    for row, family in enumerate(families):
        y = len(families) - 1 - row
        ax.text(-0.15, y + 0.5, family.name, ha="right", va="center",
                fontweight="bold", color=INK.base)
        for col, role in enumerate(_ROLES):
            color = getattr(family, role)
            if color is None:
                continue
            ax.add_patch(Rectangle((col, y), 0.92, 0.9, facecolor=color,
                                   edgecolor="none"))
            ax.text(col + 0.46, y + 0.45, color, ha="center", va="center",
                    fontsize=6, color=_label_color(color))

    for col, role in enumerate(_ROLES):
        ax.text(col + 0.46, len(families) + 0.12, role, ha="center",
                va="bottom", fontsize=7, color=INK.base)

    ax.set_xlim(-1.35, len(_ROLES))
    ax.set_ylim(0, len(families) + 0.55)
    ax.set_axis_off()
    fig.tight_layout()
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

    fig.tight_layout()
    return fig


def plot_demo(figsize_key: str = "single") -> Figure:
    """
    The base tones in use: lines, filled bands and markers.

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
    families = list(SCHEME.values())
    fig, (ax_line, ax_bar) = plt.subplots(
        1, 2, figsize=get_figsize(figsize_key)
    )

    x = np.linspace(0, 2 * np.pi, 200)
    for i, family in enumerate(families):
        y = np.sin(x - i * np.pi / len(families))
        ax_line.plot(x, y, color=family.base, label=family.name)
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

    fig.tight_layout()
    return fig


def save_previews(figure_path: str | Path,
                  figsize_key: str = "single",
                  prefix: str = "colorscheme",
                  close: bool = True) -> dict[str, Figure]:
    """
    Render all three previews and write them to `figure_path`.

    Parameters
    ----------
    figure_path : str or Path
        Existing directory to write into. Each figure is written as
        png, pdf and svg by :func:`phd_ui.plotting.save_figure`.
    figsize_key : str, optional
        Key into the shared figure-size table, passed to each plot.
    prefix : str, optional
        Filename prefix; the views are suffixed ``_swatches``,
        ``_ramps`` and ``_demo``.
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
    directory = Path(figure_path)
    if not directory.is_dir():
        raise FileNotFoundError(f"Not a directory: {directory}")

    figures: dict[str, Figure] = {
        "swatches": plot_swatches(figsize_key),
        "ramps": plot_ramps(figsize_key),
        "demo": plot_demo(figsize_key),
    }
    for view, fig in figures.items():
        save_figure(fig, directory, f"{prefix}_{view}")
        if close:
            plt.close(fig)
    return figures
