import colorsys
import logging
from typing import Iterable, Literal, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

RGBInt = Tuple[int, int, int]
RGBFloat = Tuple[float, float, float]
Mode = Literal["int", "float"]
SaturationMode = Literal["absolute", "relative"]


def hex_to_rgb(hex_color: str, mode: Mode = "int") -> Union[RGBInt, RGBFloat]:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"Expected 6-digit hex color, got '{hex_color}'")

    rgb_int: RGBInt = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    if mode == "int":
        return rgb_int
    if mode == "float":
        return (rgb_int[0] / 255.0, rgb_int[1] / 255.0, rgb_int[2] / 255.0)

    logger.error("Invalid mode '%s' in hex_to_rgb", mode)
    raise ValueError("mode must be 'int' or 'float'")


def rgb_to_hex(rgb: Union[RGBInt, RGBFloat], mode: Mode = "int") -> str:
    if mode == "int":
        r, g, b = (int(c) for c in rgb)
    elif mode == "float":
        # round + clip so values just outside [0, 1] from float math don't blow up
        r, g, b = (max(0, min(255, round(c * 255))) for c in rgb)
    else:
        logger.error("Invalid mode '%s' in rgb_to_hex", mode)
        raise ValueError("mode must be 'int' or 'float'")

    return f"#{r:02x}{g:02x}{b:02x}"


def adjust_saturation(hex_color: str,
                      value: float,
                      mode: SaturationMode = "relative") -> str:
    """
    Adjust color saturation.

    Parameters
    ----------
    hex_color : str
        Hex color code (e.g., '#ff8c00').
    value : float
        Target saturation in [0, 1] when mode='absolute',
        or a multiplicative factor when mode='relative'.
    mode : {'absolute', 'relative'}
    """
    r, g, b = hex_to_rgb(hex_color, mode="float")
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    if mode == "absolute":
        s_new = value
    elif mode == "relative":
        s_new = s * value
    else:
        raise ValueError("mode must be 'absolute' or 'relative'")

    s_new = min(1.0, max(0.0, s_new))
    return rgb_to_hex(colorsys.hsv_to_rgb(h, s_new, v), mode="float")


def create_saturation_palette(hex_color: str,
                              n_colors: int = 5,
                              sat_range: Tuple[float, float] = (0.3, 1.0)) -> list[str]:
    """
    Create a palette of colors with varying absolute saturation.
    """
    if n_colors < 2:
        raise ValueError("n_colors must be >= 2")
    s_min, s_max = sat_range
    if not (0.0 <= s_min <= s_max <= 1.0):
        raise ValueError("sat_range must satisfy 0 ≤ min ≤ max ≤ 1")

    saturations = np.linspace(s_min, s_max, n_colors)
    return [adjust_saturation(hex_color, float(s), mode="absolute") for s in saturations]