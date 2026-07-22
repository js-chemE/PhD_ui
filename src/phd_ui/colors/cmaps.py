import colorsys
from typing import Iterable, Union

import numpy as np
import matplotlib as mpl
from matplotlib.colors import Colormap, LinearSegmentedColormap, to_rgb

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


def create_colormap_from_cmap(cmap: Union[str, Colormap],
                              vmin: float = 0.0,
                              vmax: float = 1.0,
                              number: int = 10,
                              as_hex: bool = False) -> Union[list[str], LinearSegmentedColormap]:
    """
    Build a colormap by sampling an existing matplotlib colormap.

    Parameters
    ----------
    cmap : str or Colormap
        Name of a matplotlib colormap (e.g. 'viridis', 'plasma', 'berlin'),
        or a colormap instance.
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

    base_cmap = mpl.colormaps[cmap] if isinstance(cmap, str) else cmap
    positions = np.linspace(vmin, vmax, number)
    colors = base_cmap(positions)[:, :3]   # (N, 3) float array, drop alpha

    name = cmap if isinstance(cmap, str) else cmap.name
    return _finalize([tuple(c) for c in colors], f"{name}_truncated", as_hex)


def value_to_color(value: Union[float, Iterable[float], np.ndarray],
                   cmap: Union[str, Colormap],
                   vmin: float = 0.0,
                   vmax: float = 1.0,
                   cmap_vmin: float = 0.0,
                   cmap_vmax: float = 1.0,
                   clip: bool = True,
                   as_hex: bool = False) -> Union[str, list[str], tuple[float, float, float], np.ndarray]:
    """
    Map a value (or array of values) to a color sampled from a colormap.

    Two independent ranges are involved. `vmin`/`vmax` normalize `value`
    onto [0, 1] (values outside are clipped to the nearer bound when
    `clip` is True). That [0, 1] position is then rescaled onto
    `cmap_vmin`/`cmap_vmax`, the sub-range of the colormap's own [0, 1]
    domain to sample from -- useful for skipping washed-out ends of a
    colormap (e.g. `cmap_vmin=0.2, cmap_vmax=0.8` on 'Greens' avoids
    near-white and near-black extremes).

    All operations are vectorized (no Python-level looping), so passing
    an array is much faster than calling this once per value.

    Parameters
    ----------
    value : float or array-like
        Value(s) to map to a color.
    cmap : str or Colormap
        Name of a matplotlib colormap, or a colormap instance. Pass an
        instance (looked up once) if calling this repeatedly in a hot
        loop with the same colormap.
    vmin, vmax : float
        Data range used to normalize and clip `value` onto [0, 1].
    cmap_vmin, cmap_vmax : float, optional
        Sub-range of the colormap's [0, 1] domain to sample from.
    clip : bool, optional
        If True (default), values outside [vmin, vmax] are clamped to
        `cmap_vmin`/`cmap_vmax`. If False, out-of-range values are left
        to matplotlib's over/under handling (see `Colormap.set_over` /
        `set_under`), still bounded by the colormap's full [0, 1] domain.
    as_hex : bool, optional
        If True, return hex color(s) instead of RGB float tuple(s)/array.

    Returns
    -------
    str, list[str], tuple[float, float, float], or np.ndarray
        A single color if `value` is a scalar, otherwise a sequence of
        colors matching the shape of `value`. Hex string(s) if `as_hex`
        is True, else RGB float tuple(s) in [0, 1] (alpha is dropped).

    Raises
    ------
    ValueError
        If `vmin >= vmax`, or if `cmap_vmin`/`cmap_vmax` do not satisfy
        ``0 <= cmap_vmin < cmap_vmax <= 1``.
    """
    if vmin >= vmax:
        raise ValueError("vmin must be < vmax")
    if not (0.0 <= cmap_vmin < cmap_vmax <= 1.0):
        raise ValueError("cmap_vmin and cmap_vmax must satisfy 0 ≤ cmap_vmin < cmap_vmax ≤ 1")

    cmap_obj = mpl.colormaps[cmap] if isinstance(cmap, str) else cmap

    is_scalar = np.isscalar(value)
    values = np.atleast_1d(np.asarray(value, dtype=float))

    norm = (values - vmin) / (vmax - vmin)
    if clip:
        norm = np.clip(norm, 0.0, 1.0)

    positions = cmap_vmin + norm * (cmap_vmax - cmap_vmin)
    rgba = cmap_obj(positions)
    rgb = rgba[..., :3]

    if as_hex:
        hex_colors = [rgb_to_hex(tuple(c), mode="float") for c in rgb]
        return hex_colors[0] if is_scalar else hex_colors

    if is_scalar:
        return tuple(rgb[0])
    return rgb