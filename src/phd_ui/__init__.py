import phd_ui.fonts as fonts
import phd_ui.plotting as plotting
import phd_ui.colors as colors

import matplotlib.pyplot as plt
from pathlib import Path

__all__ = [
    "fonts",
    "plotting",
    "colors"
]

BASE_DIR = Path(__file__).resolve().parent

# Load custom fonts and update matplotlib parameters
FONTS_DIR = BASE_DIR / ".." / ".." / "fonts"
fonts.load_fonts(FONTS_DIR)

# Set plotting parameters
plt.rcParams.update(plotting.PARAMS["single"])