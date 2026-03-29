import colorsys
from typing import Tuple, Literal

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

RGBInt = Tuple[int, int, int]
RGBFloat = Tuple[float, float, float]
Mode = Literal["int", "float"]

def hex_to_rgb(hex_color: str, mode: Mode = "int") -> RGBInt | RGBFloat:

    hex_color = hex_color.lstrip('#')
    rgb_int: RGBInt = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))  # type: ignore

    if mode == "int":
        return rgb_int
    elif mode == "float":
        return tuple(c / 255.0 for c in rgb_int)  # type: ignore
    else:
        logger.error(f"Invalid mode '{mode}' in hex_to_rgb")
        raise ValueError("mode must be 'int' or 'float'")


def rgb_to_hex(rgb: RGBInt | RGBFloat, mode: Mode = "int") -> str:

    if mode == "int":
        r, g, b = rgb  # type: ignore
    elif mode == "float":
        r, g, b = (int(c * 255) for c in rgb)  # type: ignore
    else:
        logger.error(f"Invalid mode '{mode}' in rgb_to_hex")
        raise ValueError("mode must be 'int' or 'float'")

    return f"#{r:02x}{g:02x}{b:02x}"


def adjust_saturation_absolute(hex_color, saturation):
    """
    Adjust color saturation to an absolute value.
    
    Parameters:
    -----------
    hex_color : str
        Hex color code (e.g., "#ff8c00")
    saturation : float
        Target saturation value between 0 (grayscale) and 1 (full saturation)
        
    Returns:
    --------
    str : Adjusted hex color
    """
    # Convert hex to RGB
    r, g, b = hex_to_rgb(hex_color)
    
    # Convert RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    
    # Set new saturation (clamp between 0 and 1)
    s_new = max(0.0, min(1.0, saturation))
    
    # Convert back to RGB and then hex
    r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s_new, v)
    
    return rgb_to_hex((r_new, g_new, b_new))

def adjust_saturation_relative(hex_color, factor):
    """
    Adjust color saturation by a relative factor.
    
    Parameters:
    -----------
    hex_color : str
        Hex color code (e.g., "#ff8c00")
    factor : float
        Multiplication factor for saturation
        factor > 1: increase saturation
        factor < 1: decrease saturation
        factor = 1: no change
        
    Returns:
    --------
    str : Adjusted hex color
    """
    # Convert hex to RGB
    r, g, b = hex_to_rgb(hex_color)
    
    # Convert RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    
    # Adjust saturation relatively (clamp between 0 and 1)
    s_new = max(0.0, min(1.0, s * factor))
    
    # Convert back to RGB and then hex
    r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s_new, v)
    
    return rgb_to_hex((r_new, g_new, b_new))

def adjust_saturation(hex_color, value, mode='relative'):
    """
    Universal function to adjust color saturation.
    
    Parameters:
    -----------
    hex_color : str
        Hex color code (e.g., "#ff8c00")
    value : float
        - If mode='absolute': target saturation (0-1)
        - If mode='relative': multiplication factor
    mode : str, optional
        'absolute' or 'relative' (default: 'relative')
        
    Returns:
    --------
    str : Adjusted hex color
    """
    if mode == 'absolute':
        return adjust_saturation_absolute(hex_color, value)
    elif mode == 'relative':
        return adjust_saturation_relative(hex_color, value)
    else:
        raise ValueError("mode must be 'absolute' or 'relative'")

def create_saturation_palette(hex_color, n_colors=5, sat_range=(0.3, 1.0)):
    """
    Create a palette of colors with varying saturation.
    
    Parameters:
    -----------
    hex_color : str
        Base hex color code
    n_colors : int
        Number of colors in palette
    sat_range : tuple
        (min_saturation, max_saturation) range
        
    Returns:
    --------
    list : List of hex colors with varying saturation
    """
    saturations = np.linspace(sat_range[0], sat_range[1], n_colors)
    return [adjust_saturation_absolute(hex_color, sat) for sat in saturations]