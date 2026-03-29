import colorsys
from matplotlib.colors import LinearSegmentedColormap
from ui.colors.manipulation import rgb_to_hex
import matplotlib.pyplot as plt
from typing import Optional

def create_colormap_from_color(color: str,
                               min_sat: float,
                               max_sat: float,
                               number: int,
                               location: float,
                               as_hex: bool = False):
    """
    Build a colormap by varying saturation around a given base color.

    Parameters
    ----------
    color : str
        Hex code, e.g. '#3a7bd5'.
    min_sat : float
        Minimum saturation (0–1).
    max_sat : float
        Maximum saturation (0–1).
    number : int
        Number of colors.
    location : float
        Position in the colormap (0–1) where the original color should sit.
    as_hex : bool
        If True, return a list of hex colors instead of a colormap.
    """

    # --- hex → RGB [0..1] ---
    color = color.lstrip("#")
    r = int(color[0:2], 16) / 255.0
    g = int(color[2:4], 16) / 255.0
    b = int(color[4:6], 16) / 255.0

    # --- RGB → HSV ---
    h, s_base, v = colorsys.rgb_to_hsv(r, g, b)

    # Target saturation for the base color
    target_sat = min_sat + location * (max_sat - min_sat)

    # Adjust base color’s saturation
    r_adj, g_adj, b_adj = colorsys.hsv_to_rgb(h, target_sat, v)

    # Build saturation sweep
    sats = [
        min_sat + i * (max_sat - min_sat) / (number - 1)
        for i in range(number)
    ]

    # Convert HSV sweep → RGB
    colors = [
        colorsys.hsv_to_rgb(h, sat, v)
        for sat in sats
    ]

    # Force base color into its correct location
    idx = int(round(location * (number - 1)))
    colors[idx] = (r_adj, g_adj, b_adj)

    if as_hex:
        return [rgb_to_hex(c) for c in colors]

    # Else return a matplotlib colormap
    cmap = LinearSegmentedColormap.from_list("custom_map", colors, N=number)
    return cmap




def create_colormap_from_cmap(cmap: str,
                              vmin: Optional[float] = 0.0,
                              vmax: Optional[float] = 1.0,
                              number: Optional[int] = 10,
                              as_hex: bool = False):
    """
    Build a colormap by sampling an existing matplotlib colormap.

    Parameters
    ----------
    cmap : str
        Name of a matplotlib colormap (e.g. 'viridis', 'plasma').
    vmin : float
        Lower bound in [0, 1] for sampling the colormap.
    vmax : float
        Upper bound in [0, 1] for sampling the colormap.
    number : int
        Number of colors.
    as_hex : bool
        If True, return a list of hex colors instead of a colormap.
    """

    if not (0.0 <= vmin < vmax <= 1.0):
        raise ValueError("vmin and vmax must satisfy 0 ≤ vmin < vmax ≤ 1")

    # Get base colormap
    base_cmap = plt.get_cmap(cmap)

    # Sample positions
    positions = [
        vmin + i * (vmax - vmin) / (number - 1)
        for i in range(number)
    ]

    # Sample RGB (ignore alpha)
    colors = [
        base_cmap(p)[:3]
        for p in positions
    ]

    if as_hex:
        return [rgb_to_hex(c) for c in colors]

    return LinearSegmentedColormap.from_list(
        f"{cmap}_truncated",
        colors,
        N=number
    )
