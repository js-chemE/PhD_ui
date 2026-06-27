import colorsys
from typing import Union

import numpy as np
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap, to_rgb

from phd_ui.colors.manipulation import rgb_to_hex


def _finalize(colors: list[tuple[float, float, float]],
              name: str,
              as_hex: bool) -> Union[list[str], LinearSegmentedColormap]:
    """
    Convert a list of float RGB tuples into a colormap or hex list.

    Parameters
    ----------
    colors : list[tuple[float, float, float]]
        RGB colors with components in [0, 1].
    name : str
        Name to assign to the resulting colormap.
    as_hex : bool
        If True, return a list of hex colors instead of a colormap.

    Returns
    -------
    list[str] or LinearSegmentedColormap
        Hex colors if `as_hex` is True, otherwise a colormap built
        from `colors`.
    """
    if as_hex:
        return [rgb_to_hex(c, mode="float") for c in colors]
    return LinearSegmentedColormap.from_list(name, colors, N=len(colors))


def create_colormap_from_color(color: str,
                               min_sat: float,
                               max_sat: float,
                               number: int,
                               location: float,
                               as_hex: bool = False) -> Union[list[str], LinearSegmentedColormap]:
    """
    Build a colormap by varying saturation around a given base color.

    Parameters
    ----------
    color : str
        Hex code, e.g. '#3a7bd5'.
    min_sat, max_sat : float
        Saturation range (0–1).
    number : int
        Number of colors (must be >= 2).
    location : float
        Position in the colormap (0–1) where the original hue sits at its
        target saturation.
    as_hex : bool, optional
        If True, return a list of hex colors instead of a colormap.

    Returns
    -------
    list[str] or LinearSegmentedColormap
        Hex colors if `as_hex` is True, otherwise a colormap.

    Raises
    ------
    ValueError
        If `number` is less than 2, if `min_sat`/`max_sat` do not satisfy
        ``0 <= min_sat < max_sat <= 1``, or if `location` is outside
        ``[0, 1]``.
    """
    if number < 2:
        raise ValueError("number must be >= 2")
    if not (0.0 <= min_sat < max_sat <= 1.0):
        raise ValueError("min_sat and max_sat must satisfy 0 ≤ min_sat < max_sat ≤ 1")
    if not (0.0 <= location <= 1.0):
        raise ValueError("location must be in [0, 1]")

    r, g, b = to_rgb(color)              # handles '#rrggbb', named colors, etc.
    h, _, v = colorsys.rgb_to_hsv(r, g, b)

    sats = np.linspace(min_sat, max_sat, number)
    colors = [colorsys.hsv_to_rgb(h, s, v) for s in sats]

    # Pin the base hue at its target saturation to the requested location.
    idx = int(round(location * (number - 1)))
    target_sat = min_sat + location * (max_sat - min_sat)
    colors[idx] = colorsys.hsv_to_rgb(h, target_sat, v)

    return _finalize(colors, "custom_map", as_hex)


def create_colormap_from_cmap(cmap: str,
                              vmin: float = 0.0,
                              vmax: float = 1.0,
                              number: int = 10,
                              as_hex: bool = False) -> Union[list[str], LinearSegmentedColormap]:
    """
    Build a colormap by sampling an existing matplotlib colormap.

    Parameters
    ----------
    cmap : str
        Name of a matplotlib colormap (e.g. 'viridis', 'plasma', 'berlin').
    vmin, vmax : float
        Sampling range in [0, 1].
    number : int, optional
        Number of colors (must be >= 2).
    as_hex : bool, optional
        If True, return a list of hex colors instead of a colormap.

    Returns
    -------
    list[str] or LinearSegmentedColormap
        Hex colors if `as_hex` is True, otherwise a colormap.

    Raises
    ------
    ValueError
        If `number` is less than 2 or if `vmin`/`vmax` do not satisfy
        ``0 <= vmin < vmax <= 1``.
    """
    if number < 2:
        raise ValueError("number must be >= 2")
    if not (0.0 <= vmin < vmax <= 1.0):
        raise ValueError("vmin and vmax must satisfy 0 ≤ vmin < vmax ≤ 1")

    base_cmap = mpl.colormaps[cmap]
    positions = np.linspace(vmin, vmax, number)
    colors = base_cmap(positions)[:, :3]   # (N, 3) float array, drop alpha

    return _finalize([tuple(c) for c in colors], f"{cmap}_truncated", as_hex)